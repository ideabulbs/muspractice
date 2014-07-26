import datetime
import time
import django
from django.test import TestCase
from models import Phrase, Schedule, MetronomeSetup, Tag, Repetition
from dao import DatabaseHandler
from django.utils.timezone import utc

class Helper(object):

    @classmethod
    def _create_phrase(cls):
        tag1 = Tag()
        tag1.name = 'tag1'
        tag2 = Tag()
        tag2.name = 'tag2'
        tag3 = Tag()
        tag3.name = 'tag3'

        tag1.save()
        tag2.save()
        tag3.save()
        
        phrase = Phrase()
        unique_token = "%.6f" % time.time()
        phrase.name = 'test_phrase_%s' % unique_token
        phrase.filename = "%s.mp3" % unique_token
        phrase.image = "%s.png" % unique_token
        phrase.from_position = 10.0
        phrase.to_position = 20.0
        phrase.loop = True
        phrase.speed = 80
        phrase.pitch = 2
        phrase.volume = 100
        phrase.comment = "Test comment %s" % unique_token

        phrase.save()
        phrase.tags.add(tag1)
        phrase.tags.add(tag2)
        phrase.tags.add(tag3)
        
        ms = MetronomeSetup()
        ms.speed = 100
        ms.speed_increment = 0
        ms.duration = 300
        ms.meter = 4
        ms.volume = 95
        ms.phrase = phrase
        ms.save()

        return phrase

    @classmethod
    def _create_schedule(cls):
        schedule = Schedule()
        unique_token = "%.6f" % time.time()
        schedule.priority = 1
        schedule.comment = "Test comment for schedule %s" % unique_token
        schedule.pitch = 2
        schedule.metronome_speed = 80
        schedule.phrase_speed = 100
        next_rep_time = datetime.datetime(2020, 10, 11, 12, 10, tzinfo=utc)
        schedule.next_repetition = next_rep_time
        return schedule

    
class TestDatabase(TestCase, Helper):

    def test_phrase(self):
        dbh = DatabaseHandler()

        phrase = self._create_phrase()

        phrase_id = dbh.insert_phrase(phrase)
        assert phrase_id != None
        assert phrase_id > 0

        new_phrase = dbh.get_phrase_by_id(phrase_id)
        assert new_phrase is not None
        assert new_phrase == phrase

        new_phrase.name = "New phrase"
        dbh.update_phrase(new_phrase)
        updated_phrase = dbh.get_phrase_by_id(phrase_id)
        assert updated_phrase == new_phrase

        dbh.remove_phrase(new_phrase)
        deleted_phrase = dbh.get_phrase_by_id(phrase_id)
        assert deleted_phrase == None

        phrase1 = self._create_phrase()
        phrase2 = self._create_phrase()
        dbh.insert_phrase(phrase1)
        dbh.insert_phrase(phrase2)

        current_phrases = dbh.get_phrases(orderby="filename")
        assert len(current_phrases) == 2

    def test_schedule(self):
        dbh = DatabaseHandler()
        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)

        schedule = self._create_schedule()
        schedule.phrase = phrase
        schedule_id = dbh.insert_schedule(schedule)
        assert schedule_id != None

        new_schedule = dbh.get_schedule_by_id(schedule_id)
        assert schedule == new_schedule

        schedule1 = self._create_schedule()
        schedule1.phrase = phrase
        schedule2 = self._create_schedule()
        schedule2.phrase = phrase

        dbh.insert_schedule(schedule1)
        dbh.insert_schedule(schedule2)

        schedules = dbh.get_schedules()
        assert len(schedules) == 3
        
    def test_repetition(self):
        dbh = DatabaseHandler()

        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)

        rep = Repetition()
        rep.metronome_speed = 0
        rep.phrase = phrase
        timestamp = datetime.datetime.now()
        timestamp = timestamp.replace(tzinfo=utc)
        rep.timestamp = timestamp
        rep.pitch = 2
        rep.phrase_speed = 100
        rep.comment = "Test"
        rep.grade = 5
        rep_id = dbh.insert_repetition(rep)

        assert rep_id != None
        assert rep_id > 0
        
        new_rep = dbh.get_repetition_by_id(rep_id)
        assert new_rep == rep

        reps = dbh.get_repetitions()
        assert len(reps) == 1

        assert dbh.remove_repetition(new_rep)

        reps = dbh.get_repetitions()
        assert len(reps) == 0
        

    def test_metronome_setup(self):
        dbh = DatabaseHandler()

        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)

        assert phrase_id > 0
        
        ms = MetronomeSetup()
        ms.phrase = phrase
        ms.speed = 100
        ms.meter = 4
        ms.duration = 300
        ms.speed_increment = 2
        ms.volume = 100
        
        last_id = dbh.insert_metronome_setup(ms)
        assert last_id != None

        new_ms = dbh.get_metronome_setup_by_id(last_id)
        assert new_ms == ms

        new_ms.speed = 130
        new_ms.meter = 5
        new_ms.duration = 320
        new_ms.increment = 3
        result = dbh.update_metronome_setup(new_ms)
        assert result == True
        updated_ms = dbh.get_metronome_setup_by_id(new_ms.id)
        assert updated_ms == new_ms
        
