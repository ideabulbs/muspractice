#!/usr/bin/python
import os
from models.dbhandler import PrioritizedScheduleDatabaseHandler
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lib.settings")
import django
from app.models import Phrase, MetronomeSetup, Tag, Schedule, Repetition
from pytz import timezone
from django.utils.timezone import utc
import datetime


class Migrator(object):
    def __init__(self):
        self.dbh = PrioritizedScheduleDatabaseHandler(os.path.expanduser('~/sync/Music/bass.db'))

    def migrate(self):
        legacy_phrases = self.dbh.get_phrases()
        
        for lp in legacy_phrases:
            print lp
            p = Phrase()
            p.id = lp.id
            p.filename = lp.get_filename()
            p.from_position = lp.get_from_position()
            p.loop = True
            p.pitch = lp.get_pitch()
            p.speed = lp.get_speed()
            p.speed_increment = 0
            p.to_position = lp.get_to_position()
            p.volume = 100
            p.name = lp.get_name()
            p.image = lp.get_image()
            tagline = lp.get_tagline()
            p.save()
            for tag in tagline.split():
                tag = tag.strip()
                try:
                    new_tag = Tag.objects.get(name=tag)
                except:
                    print "Not Found:", tag
                    new_tag = Tag()
                    new_tag.name = tag
                    new_tag.save()
                p.tags.add(new_tag)
            p.comment = lp.get_comment()
            
            p.save()
            lms = self.dbh.get_metronome_setups_by_phrase_id(lp.id)
            for lm in lms:
                ms = MetronomeSetup()
                ms.id = lm.id
                ms.duration = lm.duration
                ms.speed = lm.speed
                ms.speed_increment = lm.increment
                ms.meter = lm.meter
                ms.volume = 100
                ms.phrase = p
                ms.save()

            legacy_schedules = self.dbh.get_schedules_by_phrase_id(lp.id)
            for ls in legacy_schedules:
                print ls
                s = Schedule()
                s.id = ls.id
                next_rep = ls.get_next_repetition()
                next_rep = datetime.datetime.combine(next_rep, datetime.datetime.min.time())
                next_rep = next_rep.replace(tzinfo=utc)
                s.next_repetition = next_rep
                s.comment = ls.get_comment()
                s.metronome_speed = ls.get_speed()
                s.phrase = p
                s.phrase_speed = p.speed
                s.pitch = ls.get_pitch()
                s.priority = ls.get_priority()
                s.save()

            legacy_repetitions = self.dbh.get_repetitions_by_phrase_id(p.id)
            for lr in legacy_repetitions:
                print lr
                r = Repetition()
                r.id = lr.id
                print "Old id: %d" % lr.id
                print "New id: %d" % (r.id)
                r.grade = lr.get_grade()
                r.comment = lr.get_comment()
                if lms:
                    r.metronome_speed = float(lms[0].speed)
                else:
                    r.metronome_speed = 100
                r.phrase = p
                r.phrase_speed = p.speed
                r.pitch = p.pitch
                timestamp = lr.get_date()
                print "Old date: %s" % lr.get_date()
                timestamp = datetime.datetime.combine(timestamp, datetime.datetime.min.time())
                timestamp = timestamp.replace(tzinfo=utc)
                r.timestamp = timestamp
                print "New date: %s" % r.timestamp
                r.save()
                
if __name__ == "__main__":
    m = Migrator()
    m.migrate()
