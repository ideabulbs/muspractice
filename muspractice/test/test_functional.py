import subprocess
import os
import shutil
from models.dbhandler import *
from helper import Helper
from config.config import Config

class FunctionalBase(Helper):

    dbfile = '/tmp/repetition_data.db'
    config_file = '/tmp/.muspracticerc'
    music_dir = '/tmp/muspractice'

    @classmethod
    def _populate_db(cls, dbh, phrase_count):
        phrases = []
        for _ in range(phrase_count):
            phrase = cls._create_phrase()
            phrases.append(phrase)
        # import data to the database
        delta = 1
        for phrase in phrases:
            phrase_id = dbh.insert_phrase(phrase)

            # add a schedule to every added phrase
            schedule = Schedule()
            schedule.set_phrase_id(phrase_id)

            repetition_date = datetime.date.today() + datetime.timedelta(days=delta)
            delta -= 1
            schedule.set_next_repetition(repetition_date)
            schedule_id = dbh.insert_schedule(schedule)
        return True

    def _initialize_config(self):
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
        with open(self.config_file, 'w') as out:
            data = '''[General]
audiosink = jackaudiosink
music_directory = %s
database_file = %s
temporary_directory = /tmp/
run_hooks = n
''' % (self.music_dir, self.dbfile)
            out.write(data)
        self.config = Config(self.config_file)

    def _initialize_database(self):
        if os.path.exists(self.config.DATABASE_FILE):
            os.unlink(self.config.DATABASE_FILE)
        cmd = "./muspractice -C %s -i" % (self.config_file)
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
            raise RuntimeError('Could not init test database!')

    def _create_music_directory(self):        
        if os.path.isdir(self.music_dir):
            shutil.rmtree(self.music_dir)
        os.mkdir(self.music_dir)

    def _initialize_test_data(self):
        dbh = DatabaseHandler(self.config.DATABASE_FILE)
        self.phrase_count = 10
        self._populate_db(dbh, self.phrase_count)
        
        schedules = dbh.get_schedules()
        assert len(schedules) > 0 and len(schedules) == self.phrase_count
        
    def setup(self):
        if 'EDITOR' in os.environ:
            os.environ.pop('EDITOR', None)
        self._initialize_config()
        self._create_music_directory()
        self._initialize_database()
        self._initialize_test_data()

    def teardown(self):
        if os.path.exists(self.config.DATABASE_FILE):
           os.unlink(self.config.DATABASE_FILE)
        if os.path.exists(self.config_file):
            os.unlink(self.config_file)
        if os.path.isdir(self.music_dir):
            shutil.rmtree(self.music_dir)

    def run_program(self, keys):
        cmd = "./muspractice %s" % keys
        popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
            print stderr
            raise RuntimeError("muspractice ended with an unexpected error code: %d" % popen.returncode)
        return stdout, stderr

    def reschedule(self, phrase_id, grade):
        cmd = "./muspractice -C %s -r %s" % (self.config_file, phrase_id)
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        popen.stdin.write(grade)
        stdout, stderr = popen.communicate()
        return stdout, stderr

    def get_phrase_list_length(self):
        keys = "-C %s -l" % self.config_file
        stdout, stderr = self.run_program(keys)
        length = len(stdout.strip().split(os.linesep))
        return length

    def get_todo_list_length(self):
        keys = "-C %s -t" % self.config_file
        stdout, stderr = self.run_program(keys)
        length = len(stdout.split(os.linesep))
        return length

    def get_repetition_list_length(self):
        keys = "-C %s -R" % self.config_file
        stdout, stderr = self.run_program(keys)
        length = len(stdout.split(os.linesep))
        return length

    def get_metronome_list_length(self):
        keys = "-C %s -M" % self.config_file
        stdout, stderr = self.run_program(keys)
        length = len(stdout.split(os.linesep))
        return length

 
class TestFunctional(FunctionalBase):

    remove_files = []
    
    def teardown(self):
        FunctionalBase.teardown(self)
        if self.remove_files:
            for f in self.remove_files:
                if os.path.exists(f):
                    os.unlink(f)
            del self.remove_files[:]
    
    def test_list(self):
        keys = "-C %s -l" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert len(stderr) == 0

    def test_todo(self):
        keys = "-C %s -t" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert len(stderr) == 0

    def test_show_phrase(self):
        keys = "-C %s -s 1" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert len(stderr) == 0
        assert "File:" in stdout
        assert "From:" in stdout
        assert "To:" in stdout

    def test_deactivate_phrase(self):
        original_todo_list_length = self.get_todo_list_length()
        keys = "-C %s -x 2" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        current_list_length = self.get_todo_list_length()
        assert current_list_length == original_todo_list_length - 1

    def test_reactivate_phrase(self):
        original_todo_list_length = self.get_todo_list_length()
        phrase_id = "9"
        keys = "-C %s -x %s" % (self.config_file, phrase_id)
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0

        keys = "-C %s -X" % self.config_file
        stdout, stderr = self.run_program(keys)
        initial_deactivated_list_length = len(stdout.split(os.linesep))
        stdout, stderr = self.reschedule(phrase_id, "3")
        assert not stderr
        stdout, stderr = self.run_program(keys)
        current_deactivated_list_length = len(stdout.split(os.linesep))
        assert current_deactivated_list_length == initial_deactivated_list_length - 1
        

    def test_list_deactivated(self):
        keys = "-C %s -x 2" % self.config_file
        stdout, stderr = self.run_program(keys)
        keys = "-C %s -X" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert "2" in stdout
        assert "DEACTIVATED" in stdout

    def test_list_repetitions(self):
        # create repetition data: reschedule several phrases
        for item in ['5', '6', '7']:
                self.reschedule(item, '3')
        keys = "-C %s -R" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) >= 3

    def test_reschedule(self):
        stdout, stderr = self.reschedule("3", "3")
        assert "Next repetition" in stdout

    def test_delete(self):
        keys = "-C %s -D 4" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        assert "Phrase removed" in stdout

    def test_help(self):
        keys = "-h"
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        assert "Usage" in stdout

    def test_edit(self):
        original_phrase_list_length = self.get_phrase_list_length()
        keys = "-C %s -e 9" % self.config_file
        stdout, stderr = self.run_program(keys)
        current_phrase_list_length = self.get_phrase_list_length()

        assert len(stderr) == 0
        assert original_phrase_list_length == current_phrase_list_length

    def test_create(self):
        original_phrase_list_length = self.get_phrase_list_length()
        original_todo_list_length = self.get_phrase_list_length()
        original_metronome_list_length = self.get_metronome_list_length()

        keys = "-C %s -c" % self.config_file
        stdout, stderr = self.run_program(keys)

        current_phrase_list_length = self.get_phrase_list_length()
        current_todo_list_length = self.get_phrase_list_length()
        current_metronome_list_length = self.get_metronome_list_length()

        assert len(stderr) == 0
        assert current_phrase_list_length == original_phrase_list_length + 1
        assert current_todo_list_length == original_todo_list_length + 1
        assert current_metronome_list_length == original_metronome_list_length + 1

    def test_metronome_list(self):
        original_metronome_list_length = self.get_metronome_list_length()
        keys = "-C %s -c" % self.config_file
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        current_metronome_list_length = self.get_metronome_list_length()
        assert current_metronome_list_length == original_metronome_list_length + 1


class TestBulkAdd(FunctionalBase):

    remove_files = []
    remove_directories = []
    
    def teardown(self):
        FunctionalBase.teardown(self)
        if self.remove_files:
            for f in self.remove_files:
                if os.path.exists(f):
                    os.unlink(f)
            del self.remove_files[:]
            
        if self.remove_directories:
            for d in self.remove_directories:
                if os.path.exists(d):
                    shutil.rmtree(d)
            del self.remove_directories[:]

    def test_bulk_add(self):
        """
        Add 3 files in bulk mode and verify that they are added
        """
        config = Config(self.config_file)            
        rel_dir = 'testdir'
        full_path = '%s%s' % (config.MUSIC_DIRECTORY, rel_dir)
        self.remove_directories.append(full_path)
        if not os.path.exists(full_path):
            os.mkdir(full_path)

        cmds = ["touch %s/001.png" % full_path,
                "touch %s/002.png" % full_path,
                "touch %s/003.png" % full_path]
        for cmd in cmds:
            popen = subprocess.Popen(cmd, shell=True)
            popen.communicate()
            if popen.returncode != 0:
                raise RuntimeError('Could not execute command %s' % cmd)

        initial_phrase_count = self.get_phrase_list_length()
        keys = '-C %s -b %s --tagline "test tags"' % (self.config_file, rel_dir)
        stdout, stderr = self.run_program(keys)
        current_phrase_count = self.get_phrase_list_length()
        assert current_phrase_count == initial_phrase_count + 3
        
