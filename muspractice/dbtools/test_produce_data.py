import sqlite3
from models.dbhandler import *
from models.Schedule import *
from models.Scheduler import *
from models.Repetition import *
from config.config import Config
import os
import datetime

class TestProduceData(object):
	dbfile = 'data.db'
	xmlfile = 'test/data/pypractice.xml'	

	def setup(self):
		if os.path.exists(self.dbfile):
			os.unlink(self.dbfile)
			
	def test_produce_data(self):
		dbh = DatabaseHandler(self.dbfile)
		dbh.init_database()
		dh = DataHandler(self.xmlfile)
		phrases = dh.read_phrases()

		delta = 1
		for phrase in phrases:
			phrase_id = dbh.insert_phrase(phrase)
			schedule = Schedule()
			schedule.set_phrase_id(phrase_id)
			
			repetition_date = datetime.date.today() + datetime.timedelta(days=delta)
			delta += 1
			schedule.set_next_repetition(repetition_date)
			schedule_id = dbh.insert_schedule(schedule)

		schedules = dbh.get_schedules()
		assert len(schedules) > 0 and len(schedules) == len(phrases)
		
		# phrase = phrases[0]
		# phrase_id = dbh.insert_phrase(phrase)

		# schedule = Schedule()
		# schedule.set_phrase_id(phrase_id)
		# schedule_id = dbh.insert_schedule(schedule)
		# assert schedule_id != None

		# new_schedule = dbh.get_schedule_by_id(schedule_id)
		# assert schedule == new_schedule

		# schedule1 = Schedule()
		# schedule1.set_phrase_id(phrase_id)
		# schedule2 = Schedule()
		# schedule2.set_phrase_id(phrase_id)

		# dbh.insert_schedule(schedule1)
		# dbh.insert_schedule(schedule2)

		# schedules = dbh.get_schedules()
		# assert len(schedules) == 3
