#!/usr/bin/python3
import sys
import os
import time
import datetime
import random
import configparser
import glob
import subprocess
from optparse import OptionParser
from mutagen.mp3 import MP3
from .tools.Pipeline import *
from .models.dbhandler import PrioritizedScheduleDatabaseHandler
from .models.Schedule import *
from .models.Scheduler import *
from .models.Repetition import *
from .models.MetronomeSetup import *
from .models.IniSerializator import *
from .tools.Metronome import Metronome
from .tools.SightRead import SightRead
from .tools.Hook import run_hooks, wait_hooks
from .config.config import Config



def create_context(phrase, metronome=None):
    context = dict()
    context = {
        'PHRASE_ID': phrase.id,
        'PHRASE_NAME': phrase.get_name(),
        'PHRASE_PITCH': phrase.get_pitch(),
        'PHRASE_FROM_POSITION': phrase.get_from_position(),
        'PHRASE_TO_POSITION': phrase.get_to_position(),
        'PHRASE_FILENAME': phrase.get_filename(),
        'PHRASE_IMAGE': phrase.get_image()
        }
    if metronome is not None:
        context['PHRASE_METRONOME_SPEED'] = metronome.speed
    else:
        context['PHRASE_SPEED'] = phrase.get_speed()        
    return context


class TextInterface(object):
    '''muspractice text console UI'''

    def __init__(self, config_file):
        '''Constructor'''
        self.config = Config(config_file)
        if self.config.is_new:
            print("New config has been initialized. Verify settings: %s" % config_file)
            sys.exit(0)

    def init_dbhandler(self, database):
        '''Initialize database handler'''
        self.dbh = PrioritizedScheduleDatabaseHandler(database)
                        
    def list_phrases(self):
        phrases = self.dbh.get_phrases(orderby='id')
        for phrase in phrases:
            schedules = self.dbh.get_schedules_by_phrase_id(phrase.id, orderby='next_repetition')
            print(phrase.id, '\t', phrase.get_filename(path=False), "\t", phrase.get_short_description(), "\t", phrase.get_tagline(), end=' ')
            if schedules:
                print("\t", schedules[-1].get_next_repetition())
            else:
                print()

    def play_phrase(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        metronomes = self.dbh.get_metronome_setups_by_phrase_id(phrase_id)
        if not metronomes:
            print("No metronome found for the given phrase!")
            return
        metronome = metronomes[0]

        if phrase.get_image():
            sr = self.show_image(phrase, metronome)

        if phrase.get_comment():
            print()
            print(phrase.get_comment())
            print()

        pre_hooks = []
        context = create_context(phrase)
        if self.config.RUN_HOOKS == 'y':
            pre_hooks = run_hooks('muspractice/hooks.pre', context=context)

        if phrase.get_filename():
            player = Pipeline(self.config.AUDIOSINK)

            if phrase.get_filename().startswith(os.sep):  # absolute path given
                media_file_path = phrase.get_filename()
            else:  # path relative to self.config.MUSIC_DIRECTORY
                media_file_path = '%s%s' % (self.config.MUSIC_DIRECTORY, phrase.get_filename())
                media_file_path = os.path.expanduser(media_file_path)
            if not os.path.exists(media_file_path):
                sys.stderr.write("Media file not found: %s\n" % media_file_path)
                return
            else:
                print("Media file found: %s " % media_file_path)

            uri = "file://%s" % os.path.expanduser(os.path.abspath(media_file_path))
            player.set_file(uri)
            player.set_from_position(phrase.get_from_position())

            # determine mp3 file length if no to_position is definied:
            to_position = phrase.get_to_position()
            if to_position == 0.0 and uri.lower().endswith('.mp3'):
                mp3 = MP3(os.path.abspath(media_file_path))
                to_position = mp3.info.length - 0.1
            elif to_position < 0.0 and uri.lower().endswith('.mp3'):
                mp3 = MP3(os.path.abspath(media_file_path))
                to_position = mp3.info.length - (to_position * (-1))
            player.set_to_position(to_position)

            speed = phrase.get_speed()
            if speed > 0:
                speed = speed / 100.0
            else:
                speed = 1.0
            player.set_speed(speed)

            if phrase.get_pitch():
                player.set_pitch(2**(phrase.get_pitch()/12.0))

            player.set_loop(True)
            player.play()
            duration = 0
            repetition = 1
            print("Duration: %d" % metronome.duration)
            try:
                while True:
                    position = player.get_position()
                    if not position:
                        continue
                    if position <= player.get_from_position() or position > player.get_to_position() or duration == 0:
                        if duration > metronome.duration:
                            break
                        print("Repetition %d" % repetition)
                        player.seek_simple(player.get_from_position())
                        repetition += 1
                    duration += 1
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
            player.pause()
            
        if phrase.get_image():
            sr.stop()

        post_hooks = []
        if self.config.RUN_HOOKS == 'y':
            post_hooks = run_hooks('muspractice/hooks.post', context=context)
            
    def show_phrase(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        if phrase:
            print()
            print("Name: %s" % phrase.get_name())
            print("File: %s" % phrase.get_filename())
            if phrase.get_image():
                print("Image: %s" % phrase.get_image())
            if phrase.get_tagline():
                print("Tags: %s" % phrase.get_tagline())
            print("From: %.2f" % phrase.get_from_position())
            print("To: %.2f" % phrase.get_to_position())
            print()
            print(phrase.get_comment())
        else:
            "Phrase not found. Wrong id?"
        metronomes = self.dbh.get_metronome_setups_by_phrase_id(phrase_id)
        if metronomes:
            ms = metronomes[0]
            print("Metronome: speed=%d; meter=%d; duration=%d; increment=%d" % (ms.speed, ms.meter, ms.duration, ms.increment))

    def reschedule_phrase(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        if not phrase:
            print("No phrase found with the given id: %d" % phrase_id)
            return
        repetitions = self.dbh.get_repetitions_by_phrase_id(phrase_id)
        scheduler = Scheduler()
        while True:
            user_input = input("Enter new grade (0-5): ")
            try:
                grade = int(user_input)
                if grade in range(0,6):
                    break
            except ValueError:
                continue
        current_repetition = Repetition()
        current_repetition.set_date(datetime.date.today())
        current_repetition.set_grade(grade)
        current_repetition.set_phrase_id(phrase.id)

        self.dbh.insert_repetition(current_repetition)

        past_schedules = self.dbh.get_schedules_by_phrase_id(phrase_id)
        if past_schedules:
            for schedule in past_schedules:
                if not self.dbh.remove_schedule(schedule):
                    print("Failed to remove old schedule: %d" % (schedule.id))

        schedule = scheduler.get_new_schedule(phrase, grade, repetition_list=repetitions)
        print("Next repetition: %s" % schedule.get_next_repetition())
        self.dbh.insert_schedule(schedule)

        metronomes = self.dbh.get_metronome_setups_by_phrase_id(phrase_id)
        if metronomes:
            ms = metronomes[0]
            if ms.increment and ms.speed != 0:
                ms.speed += ms.increment
            if not self.dbh.update_metronome_setup(ms):
                print("Failed to update the metronome setup")

    def show_todo_list(self):
        schedules = self.dbh.get_active_schedules(orderby="next_repetition")
        schedules.reverse()
        for schedule in schedules:
            phrase = self.dbh.get_phrase_by_id(schedule.get_phrase_id())
            if not phrase:
                print("Inconsistent database!")
                return
            if schedule.get_priority() is not None:
                priority = "%.1f" % schedule.get_priority()
            else:
                priority = None
            if priority:
                description = phrase.get_name()
                if not description:
                    description = phrase.get_short_description()
                print(phrase.id, "\t", priority, "\t", phrase.get_filename(path=False), description, "\t", phrase.get_tagline())

    def edit_phrase_inkscape(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        if not phrase.get_image():
            print("The given phrase has no image")
            return False

        img_path = "%s%s" % (self.config.MUSIC_DIRECTORY, phrase.get_image())
        ann_path = "%s%s" % (self.config.MUSIC_DIRECTORY, phrase.get_annotated_image())
        if not os.path.exists(os.path.expanduser(img_path)):
            print("Cannot find image: %s" % img_path)
            return False

        path = img_path
        if os.path.exists(os.path.expanduser(ann_path)):
            path = ann_path

        cmd = "inkscape %s" % path
        popen = subprocess.Popen(cmd, shell=True)
        popen.communicate()
        return True

    def edit_phrase(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        metronome_setups = self.dbh.get_metronome_setups_by_phrase_id(phrase_id)
        if not phrase and not metronome_setups:
            print("No phrase or metronome found")
            return False
        tempfile = '%sdata_%.2f.ini' % (self.config.TEMPORARY_DIRECTORY, time.time())

        if not metronome_setups:
            metronome_setup = MetronomeSetup()
            metronome_setup.phrase_id = phrase_id
            metronome_setup.speed = 100
            metronome_setup.meter = 0
            metronome_setup.duration = 300
            metronome_setup.increment = 0
            ms_id = self.dbh.insert_metronome_setup(metronome_setup)
            metronome_setup.id = ms_id
        else:
            metronome_setup = metronome_setups[0]
        pis = IniSerializator(tempfile, phrase=phrase, metronome_setup=metronome_setup)
        if not pis.write():
            print("Unable to write temporary file: %s" % tempfile)
            return
        if not 'EDITOR' in os.environ:
            print("Can't find suitable editor. Set the EDITOR environment variable!")
        else:
            os.system("%s %s" % (os.environ['EDITOR'], tempfile))
        updated_result = pis.read()
        updated_phrase = updated_result['Phrase']
        updated_metronome_setup = updated_result['MetronomeSetup']
        if updated_phrase:
            if not self.dbh.update_phrase(updated_phrase):
                print("Can't update the phrase")
            else:
                print("Phrase updated")
        if updated_metronome_setup:
            if not self.dbh.update_metronome_setup(updated_metronome_setup):
                print("Can't update the metronome setup")
            else:
                print("Metronome setup updated")
        os.unlink(tempfile)
        return True

    def delete_phrase(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        if not phrase:
            print("No phrase found with the given id: %d" % phrase_id)
            return
        if not self.dbh.remove_phrase(phrase):
            print("Error occured while removing the phrase")
        else:
            print("Phrase removed: %s %s" % (phrase.get_filename(path=False), phrase.get_short_description()))

    def create_phrase(self):
        phrase = Phrase()
        phrase_id = self.dbh.insert_phrase(phrase)
        if not phrase_id:
            print("Failed to add phrase to database")
            return
        schedule = Schedule()
        schedule.set_phrase_id(phrase_id)
        schedule.set_next_repetition(datetime.date.today())
        schedule_id = self.dbh.insert_schedule(schedule)
        if not schedule_id:
            print("Failed to schedule the new phrase")
            return
        metronome_setup = MetronomeSetup()
        metronome_setup.phrase_id = phrase_id
        metronome_setup.speed = 100
        metronome_setup.meter = 0
        metronome_setup.duration = 300
        metronome_setup.increment = 2
        metronome_setup_id = self.dbh.insert_metronome_setup(metronome_setup)
        if not metronome_setup_id:
            print("Failed to insert metronome setup")
            return
        self.edit_phrase(phrase_id)

    def deactivate_phrase(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        if not phrase_id:
            print("Failed to deactivate phrase: the given phrase is not found")
            return

        past_schedules = self.dbh.get_schedules_by_phrase_id(phrase_id)
        if past_schedules:
            for schedule in past_schedules:
                if not self.dbh.remove_schedule(schedule):
                    print("Failed to remove old schedule: %d" % (schedule.id))

        schedule = Schedule()
        schedule.set_phrase_id(phrase_id)
        schedule.set_next_repetition(datetime.date(1970, 1, 1))
        schedule_id = self.dbh.insert_schedule(schedule)
        if not schedule_id:
            print("Failed to deactivate phrase id %d" % phrase_id)
            return

    def list_deactivated_phrases(self):
        schedules = self.dbh.get_inactive_schedules(orderby="next_repetition")
        schedules.reverse()
        for schedule in schedules:
            phrase = self.dbh.get_phrase_by_id(schedule.get_phrase_id())
            if not phrase:
                print("Inconsistent database!")
                return
            print(phrase.id, "\t", "DEACTIVATED", "\t", phrase.get_filename(path=False), phrase.get_short_description(), "\t", phrase.get_tagline(), '.')

    def init_database(self):
        self.dbh.init_database()

    def show_image(self, phrase, ms):
        sr = SightRead()

        img_path = "%s%s" % (self.config.MUSIC_DIRECTORY, phrase.get_image())
        ann_path = "%s%s" % (self.config.MUSIC_DIRECTORY, phrase.get_annotated_image())

        path = img_path
        if os.path.exists(os.path.expanduser(ann_path)):
            path = ann_path
        path = os.path.expanduser(path)

        print("Displaying image: %s" % path)
        sr.filename = path
        sr.duration = ms.duration
        if not sr.start():
            print("Could not show image!")
        return sr
            
    def play_metronome(self, phrase_id):
        phrase = self.dbh.get_phrase_by_id(phrase_id)
        if not phrase:
            print("No phrase found with the given id: %d" % phrase_id)
            return
        metronomes = self.dbh.get_metronome_setups_by_phrase_id(phrase_id)
        if not metronomes:
            print("No metronome found for the given phrase!")
            return
        ms = metronomes[0]

        m = Metronome()
        m.set_meter(ms.meter)
        m.set_speed(ms.speed)
        m.set_jack_ports(self.config.JACK_PORTS)
        print("Metronome tempo: %d; Meter: %s" % (ms.speed, ms.meter))
        m.set_duration(ms.duration)

        if phrase.get_image():
            sr = self.show_image(phrase, ms)

        if phrase.get_comment():
            print()
            print(phrase.get_comment())
            print()

        pre_hooks = []
        context = create_context(phrase, metronome=ms)
        if self.config.RUN_HOOKS == 'y':
            pre_hooks = run_hooks('muspractice/hooks.pre', context=context)
            
        # if speed is 0, metronome won't be started
        if ms.speed != 0:
            if not m.start():
                print("Could not start metronome!")

        try:
            time.sleep(ms.duration)
        except KeyboardInterrupt:
            pass

        # if speed is 0, metronome wasn't started and doesn't have to be stopped
        if ms.speed != 0:
            if not m.stop():
                print("Could not stop metronome!")

        if phrase.get_image():
            sr.stop()

        post_hooks = []
        if self.config.RUN_HOOKS == 'y':
            post_hooks = run_hooks('muspractice/hooks.post', context=context)

        wait_hooks(pre_hooks)
        wait_hooks(post_hooks)

    def list_repetitions(self):
        repetitions = self.dbh.get_repetitions()
        for repetition in repetitions:
            phrase = self.dbh.get_phrase_by_id(repetition.get_phrase_id())
            print(repetition.id, repetition.get_date(), "\t", repetition.get_grade(), "\t", phrase.id, "\t", phrase.get_filename(path=False), phrase.get_short_description(), ":::%s:::" % phrase.get_tagline())

    def list_metronome_setups(self):
        metronome_setups = self.dbh.get_metronome_setups()
        for metronome_setup in metronome_setups:
            phrase = self.dbh.get_phrase_by_id(metronome_setup.phrase_id)
            print(metronome_setup.id, metronome_setup.speed, metronome_setup.meter, metronome_setup.duration, phrase.get_filename(path=False), phrase.get_short_description())

    def bulk_add(self, directory, tagline):
        """
        Add multiple images/sound files to database as phrases

        @param directory: directory path relative to music dir
        """
        path = "%s%s" % (self.config.MUSIC_DIRECTORY, directory)
        exp_path = os.path.expanduser(path)
        print("exp path", exp_path)
        if not os.path.exists(os.path.expanduser(path)):
            print("Could not find specified path: %s" % path)
            return
        self.dbh.bulk_add(directory, self.config, tagline)


def main():
    parser = OptionParser()

    parser.add_option('-C', '--config', action="store",
                      type="string", dest="config",
                      help="configuration file to use. ")

    parser.add_option('-t', '--todo', action="store_true",
                      dest="todo", help="show todo list")
    
    parser.add_option('-l', '--list', action="store_true",
                      dest="list_phrases", help="list all phrases")
    
    parser.add_option('-p', '--play', action="store",
                      type="int", dest="play_phrase",
                      help="phrase id to play")
    
    parser.add_option('-s', '--show', action="store",
                      type="int", dest="show_phrase",
                      help="phrase id to show")
    
    parser.add_option('-r', '--reschedule', action="store",
                      type="int", dest="reschedule_phrase",
                      help="phrase id to (re)schedule")
    
    parser.add_option('-e', '--edit', action="store",
                      type="int", dest="edit_phrase",
                      help="phrase id to edit")
    
    parser.add_option('-E', '--edit-annotations', action="store",
                      type="int", dest="edit_phrase_inkscape",
                      help="phrase id to edit in inkscape (annotations)")

    parser.add_option('-c', '--create', action="store_true",
                      dest="create_phrase", help="create phrase")
    
    parser.add_option('-D', '--delete', action="store",
                      type="int", dest="delete_phrase", help="delete phrase")
    
    parser.add_option('-x', '--deactivate', action="store",
                      type="int", dest="deactivate_phrase",
                      help="phrase id to deactivate/suspend (exclude from todo/schedules)")
    
    parser.add_option('-X', '--list-deactivated',
                      action="store_true", dest="list_deactivated",
                      help="list phrases deactivated from scheduling")
    
    parser.add_option('-i', '--init-db', action="store_true",
                      dest="init_db", help="initialize a new database")
    
    parser.add_option('-m', '--metronome', action="store",
                      type="int", dest="metronome",
                      help="play metronome associated with the given phrase id")
    
    parser.add_option('-R', '--list-repetitions', action="store_true",
                      dest="list_repetitions", help="list repetitions")
    
    parser.add_option('-M', '--list-metronome-setups', action="store_true",
                      dest="list_metronome_setups", help="list metronome setups")

    parser.add_option('-b', '--bulk-add', action="store",
                      type="str", dest="bulk_add",
                      help="bulk add images/sound files as phrases")

    parser.add_option('--tagline', action="store",
                      type="str", dest="bulk_add_tagline",
                      help="Tag line for items added in bulk")
    
    (options, args) = parser.parse_args()
      
    
    if not options.config:
        raise RuntimeError('No config file given!')

    config = Config(options.config)

    if not os.path.exists(options.config):
        sys.stderr.write('Could not find config file: %s. Usage: ./muspractice -C <filename> -i \n' % options.config)
        sys.exit(1)

    ti = TextInterface(options.config)

    ti.init_dbhandler(config.DATABASE_FILE)
        
    if options.play_phrase:
        ti.play_phrase(options.play_phrase)
    elif options.list_phrases:
        ti.list_phrases()
    elif options.show_phrase:
        ti.show_phrase(options.show_phrase)
    elif options.reschedule_phrase:
        ti.reschedule_phrase(options.reschedule_phrase)
    elif options.todo:
        ti.show_todo_list()
    elif options.edit_phrase:
        ti.edit_phrase(options.edit_phrase)
    elif options.edit_phrase_inkscape:
        ti.edit_phrase_inkscape(options.edit_phrase_inkscape)
    elif options.create_phrase:
        ti.create_phrase()
    elif options.delete_phrase:
        ti.delete_phrase(options.delete_phrase)
    elif options.deactivate_phrase:
        ti.deactivate_phrase(options.deactivate_phrase)
    elif options.list_deactivated:
        ti.list_deactivated_phrases()
    elif options.init_db:
        ti.init_database()
    elif options.metronome:
        ti.play_metronome(options.metronome)
    elif options.list_repetitions:
        ti.list_repetitions()
    elif options.list_metronome_setups:
        ti.list_metronome_setups()
    elif options.bulk_add:
        if options.bulk_add_tagline is None:
            print("Use --tagline argument to specify tags for the items added in bulk!")
            sys.exit(1)
        ti.bulk_add(options.bulk_add, options.bulk_add_tagline)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
