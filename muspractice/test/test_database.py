import sqlite3
from django.test import TestCase
from models.dao import DatabaseHandler
from models.Schedule import *
from models.Scheduler import *
from models.Repetition import *
from models.MetronomeSetup import *
from config.config import Config
from helper import Helper
import os
import datetime


class TestDatabase(TestCase, Helper):

    def test_phrase(self):
        dbh = DatabaseHandler()
        dbh.init_database()

        phrase = self._create_phrase()

        phrase_id = dbh.insert_phrase(phrase)
        assert phrase_id != None

        new_phrase = dbh.get_phrase_by_id(phrase_id)
        assert new_phrase == phrase

        new_phrase.set_name("New phrase")
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
        dbh = DatabaseHandler(self.dbfile)
        dbh.init_database()
        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)

        schedule = Schedule()
        schedule.set_phrase_id(phrase_id)
        schedule_id = dbh.insert_schedule(schedule)
        assert schedule_id != None

        new_schedule = dbh.get_schedule_by_id(schedule_id)
        assert schedule == new_schedule

        schedule1 = Schedule()
        schedule1.set_phrase_id(phrase_id)
        schedule2 = Schedule()
        schedule2.set_phrase_id(phrase_id)

        dbh.insert_schedule(schedule1)
        dbh.insert_schedule(schedule2)

        schedules = dbh.get_schedules()
        assert len(schedules) == 3

    def test_repetition(self):
        dbh = DatabaseHandler(self.dbfile)
        dbh.init_database()

        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)

        rep = Repetition()
        rep.set_phrase_id(phrase_id)
        rep.set_date(datetime.date.today())
        rep.set_pitch(1)
        rep.set_speed(100)
        rep.set_comment("Test")
        rep.set_grade(5)
        rep_id = dbh.insert_repetition(rep)

        assert rep_id != None

        new_rep = dbh.get_repetition_by_id(rep_id)
        assert new_rep == rep

        reps = dbh.get_repetitions()
        assert len(reps) == 1

        assert dbh.remove_repetition(new_rep)

        reps = dbh.get_repetitions()
        assert len(reps) == 0

    def test_scheduler(self):
        dbh = DatabaseHandler(self.dbfile)
        dbh.init_database()

        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)

        scheduler = Scheduler()
        schedule = scheduler.get_new_schedule(phrase, 5)  # using new grade
        assert schedule != None

        # no previous repetitions => shall be repeated tomorrow
        print schedule.get_next_repetition()
        print datetime.date.today() + datetime.timedelta(days=2)
        assert datetime.date.today() + datetime.timedelta(days=1) <= schedule.get_next_repetition() <= datetime.date.today() + datetime.timedelta(days=3)

        # two previous repetitions
        r1 = Repetition()
        r1.set_date(datetime.date.today() - datetime.timedelta(days=5))
        r2 = Repetition()
        r2.set_date(datetime.date.today() - datetime.timedelta(days=3))
        schedule = scheduler.get_new_schedule(phrase, 5, repetition_list=[r1, r2])
        assert datetime.date.today() + datetime.timedelta(days=3) <= schedule.get_next_repetition() <= datetime.date.today() + datetime.timedelta(days=6)

    def test_metronome_setup(self):
        dbh = DatabaseHandler(self.dbfile)
        dbh.init_database()

        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)

        ms = MetronomeSetup()
        ms.phrase_id = 1
        ms.speed = 100
        ms.meter = 4
        ms.duration = 300
        ms.increment = 2

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

class TestPrioritizedScheduleDatabaseHandler(Helper, DatabaseTestBase):

    def test_priority(self):
        psh = PrioritizedScheduleDatabaseHandler(self.dbfile)
        psh.init_database()

        phrase_count = 5
        for p in range(phrase_count):

            phrase = self._create_phrase()
            phrase_id = psh.insert_phrase(phrase)

            schedule = self._create_schedule()
            schedule.set_next_repetition(datetime.date.today() - datetime.timedelta(days=p))
            schedule.set_phrase_id(phrase_id)
            schedule_id = psh.insert_schedule(schedule)

            repetition_count = 3
            for i in range(repetition_count):
                rep = Repetition()
                rep.set_phrase_id(phrase_id)
                rep.set_date(schedule.get_next_repetition() - datetime.timedelta(days=i * repetition_count))
                rep_id = psh.insert_repetition(rep)

        schedules = psh.get_active_schedules()
        for schedule in schedules:
            print "%.2f\t%s" % (schedule.get_priority(), schedule.get_next_repetition())
        assert schedules[0].get_priority() > schedules[1].get_priority() > schedules[2].get_priority() > schedules[3].get_priority() > schedules[4].get_priority()
