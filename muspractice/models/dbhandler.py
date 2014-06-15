import sys
import sqlite3
import libschedule
from models.Phrase import *
from models.Schedule import *
from models.Repetition import *
from models.MetronomeSetup import *

class AbstractDatabaseHandler(object):

        _con = None

	def __init__(self, db_file):
		self._con = sqlite3.connect(db_file)
		self._con.row_factory = sqlite3.Row
		self._cur = self._con.cursor()

	def init_database(self):
		self._cur.execute("CREATE TABLE Phrases("
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, filename TEXT, image TEXT, tagline TEXT, from_position FLOAT, to_position FLOAT,"
                                  "loop BOOLEAN, speed INTEGER, pitch INTEGER, comment TEXT)")

		self._cur.execute("CREATE TABLE MetronomeSetups("
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT, phrase_id INTEGER, speed INTEGER, meter INTEGER, duration INTEGER, increment INTEGER, "\
                                  "FOREIGN KEY(phrase_id) REFERENCES Phrases(id))")

		self._cur.execute("CREATE TABLE Schedules("
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT, phrase_id INTEGER, next_repetition DATE, speed INTEGER, pitch INTEGER, comment TEXT, priority INTEGER, "
                                  "FOREIGN KEY(phrase_id) REFERENCES Phrases(id))")

		self._cur.execute("CREATE TABLE Repetitions("
                                  "id INTEGER PRIMARY KEY AUTOINCREMENT, phrase_id INTEGER, repetition_date DATE, speed INTEGER, pitch INTEGER, comment TEXT, grade INTEGER, "
                                  "FOREIGN KEY(phrase_id) REFERENCES Phrases(id))")

	def get_items(self, table, orderby=None):
		if not orderby:
                        self._cur.execute("SELECT * FROM %s" % table)
		else:
                        self._cur.execute("SELECT * FROM %s ORDER BY %s" % (table, orderby))
		rows = self._cur.fetchall()
		return rows

	def get_item_by_id(self, table, item_id):
		self._cur.execute("SELECT * FROM %s WHERE id=%d" % (table, item_id))
		data = self._cur.fetchone()
		return data

	def get_items_by_related_id(self, table, related_id_name, related_id, orderby=None):
		query = "SELECT * FROM %s WHERE %s=%d" % (table, related_id_name, related_id)
		if orderby:
			query += " ORDER BY %s" % orderby
		self._cur.execute(query)
		rows = self._cur.fetchall()
		return rows

	def remove_item(self, table, item_id):
		self._cur.execute("DELETE FROM %s WHERE id=%d" % (table, item_id))
		self._con.commit()
		return True

class PhraseHandler(AbstractDatabaseHandler):

	def insert_phrase(self, phrase):
		query = '''INSERT INTO Phrases(name, filename, image, tagline, from_position, to_position, loop, speed, pitch, comment) ''' +\
		'''VALUES("%s", "%s", "%s", "%s", %.3f, %.3f, %d, %d, %d, "%s")''' % (phrase.get_name(),
                                                                                      phrase.get_filename(),
                                                                                      phrase.get_image(),
                                                                                      phrase.get_tagline(),
                                                                                      phrase.get_from_position(),
                                                                                      phrase.get_to_position(),
                                                                                      int(phrase.get_loop()),
                                                                                      phrase.get_speed(),
                                                                                      phrase.get_pitch(),
                                                                                      phrase.get_comment())
		self._cur.execute(query)
		self._con.commit()
		self._cur.execute("SELECT last_insert_rowid()")
		last_id = self._cur.fetchone()
		if last_id:
			return last_id[0]
		else:
			return None

	def remove_phrase(self, phrase):
		self._cur.execute("DELETE FROM Phrases WHERE id=%d" % phrase.id)
		self._cur.execute("DELETE FROM Schedules WHERE phrase_id=%d" % phrase.id)
		self._cur.execute("DELETE FROM Repetitions WHERE phrase_id=%d" % phrase.id)
		self._cur.execute("DELETE FROM MetronomeSetups WHERE phrase_id=%d" % phrase.id)
		self._con.commit()
		return True

	def update_phrase(self, phrase):
		self._cur.execute('''UPDATE Phrases SET name="%s",filename="%s",image="%s",tagline="%s",from_position=%.3f,to_position=%.3f,loop=%d,speed=%d,pitch=%d,comment="%s" WHERE id=%d''' % (phrase.get_name(),
																					  phrase.get_filename(),
																					  phrase.get_image(),
																					  phrase.get_tagline(),
																					  phrase.get_from_position(),
																					  phrase.get_to_position(),
																					  int(phrase.get_loop()),
																					  phrase.get_speed(),
																					  phrase.get_pitch(),
																					  phrase.get_comment(),
																					  phrase.id))
		self._con.commit()
		return True

	def get_phrase_by_id(self, phrase_id):
		self._cur.execute("SELECT * FROM Phrases WHERE id=%d" % phrase_id)
		data = self._cur.fetchone()
		if data:
			p = self._build_phrase(data)
			return p
		else:
			return None

	def get_phrases(self, orderby=None):
		if not orderby:
				self._cur.execute("SELECT * FROM Phrases")
		else:
				self._cur.execute("SELECT * FROM Phrases ORDER BY %s" % orderby)
		rows = self._cur.fetchall()
		result = []
		for row in rows:
			p = self._build_phrase(row)
			result.append(p)
		return result

	def _build_phrase(self, data):
		p = Phrase()
		p.id = data['id']
		p.set_name(data['name'])
		p.set_filename(data['filename'])
		p.set_image(data['image'])
		p.set_tagline(data['tagline'])
		p.set_from_position(data['from_position'])
		p.set_to_position(data['to_position'])
		p.set_loop(data['loop'])
		p.set_speed(data['speed'])
		p.set_pitch(data['pitch'])
		p.set_comment(data['comment'])
		return p


class ScheduleHandler(AbstractDatabaseHandler):

	def insert_schedule(self, schedule):
		self._cur.execute("INSERT INTO Schedules(phrase_id, next_repetition, speed, pitch, comment, priority) VALUES "
						  "(%d, '%s', %d, %d, '%s', %d)" % (schedule.get_phrase_id(), schedule.get_next_repetition(), schedule.get_speed(), schedule.get_pitch(), schedule.get_comment(), schedule.get_priority()))
		self._con.commit()
		self._cur.execute("SELECT last_insert_rowid()")
		last_id = self._cur.fetchone()
		if last_id:
			return last_id[0]
		else:
			return None

	def remove_schedule(self, schedule):
		self._cur.execute("DELETE FROM Schedules WHERE id=%d" % schedule.id)
		self._con.commit()
		return True

	def _build_schedule(self, data):
		s = Schedule()
		s.id = data['id']
		s.set_next_repetition(data['next_repetition'])
		s.set_phrase_id(data['phrase_id'])
		s.set_speed(data['speed'])
		s.set_pitch(data['pitch'])
		s.set_comment(data['comment'])
		s.set_priority(data['priority'])
		return s

	def get_schedule_by_id(self, schedule_id):
		self._cur.execute("SELECT * FROM Schedules WHERE id=%d" % schedule_id)
		data = self._cur.fetchone()
		if data:
			s = self._build_schedule(data)
			return s
		else:
			return None

	def get_schedules_by_phrase_id(self, phrase_id, orderby=None):
		if not orderby:
			self._cur.execute("SELECT * FROM Schedules WHERE phrase_id=%d" % phrase_id)
		else:
			self._cur.execute("SELECT * FROM Schedules WHERE phrase_id=%d ORDER BY %s" % (phrase_id, orderby))
		rows = self._cur.fetchall()
		result = []
		for row in rows:
			r = self._build_schedule(row)
			result.append(r)
		return result

	def get_schedules(self, orderby=None):
		if not orderby:
				self._cur.execute("SELECT * FROM Schedules")
		else:
				self._cur.execute("SELECT * FROM Schedules ORDER BY %s" % orderby)
		rows = self._cur.fetchall()
		result = []
		for row in rows:
			p = self._build_schedule(row)
			result.append(p)
		return result

	def get_active_schedules(self, orderby=None):
		schedules = self.get_schedules(orderby=orderby)
		result = []
		for schedule in schedules:
			if schedule.get_next_repetition() > datetime.date(1970, 1, 1):
				result.append(schedule)
		return result

	def get_inactive_schedules(self, orderby=None):
		schedules = self.get_schedules(orderby=orderby)
		result = []
		for schedule in schedules:
			if schedule.get_next_repetition() == datetime.date(1970, 1, 1):
				result.append(schedule)
		return result


class RepetitionHandler(AbstractDatabaseHandler):

	def insert_repetition(self, rep):
		self._cur.execute("INSERT INTO Repetitions(phrase_id, repetition_date, speed, pitch, comment, grade) VALUES (%d, '%s', %d, %d, '%s', %d)" % (rep.get_phrase_id(), rep.get_date(), rep.get_speed(), rep.get_pitch(), rep.get_comment(), rep.get_grade()))
		self._con.commit()
		self._cur.execute("SELECT last_insert_rowid()")
		last_id = self._cur.fetchone()
		if last_id:
			return last_id[0]
		else:
			return None

	def _build_repetition(self, data):
		r = Repetition()
		r.id = data['id']
		r.set_date(data['repetition_date'])
		r.set_phrase_id(data['phrase_id'])
		r.set_speed(data['speed'])
		r.set_pitch(data['pitch'])
		r.set_comment(data['comment'])
		r.set_grade(data['grade'])
		return r

	def get_repetition_by_id(self, repetition_id):
		data = self.get_item_by_id('Repetitions', repetition_id)
		if data:
			r = self._build_repetition(data)
			return r
		else:
			return None

	def get_repetitions(self, orderby=None):
		rows = self.get_items('Repetitions', orderby=orderby)
		result = []
		for row in rows:
			r = self._build_repetition(row)
			result.append(r)
		return result

	def get_repetitions_by_phrase_id(self, phrase_id, orderby=None):
		rows = self.get_items_by_related_id('Repetitions', 'phrase_id', phrase_id, orderby=orderby)
		result = []
		for row in rows:
			r = self._build_repetition(row)
			result.append(r)
		return result

	def remove_repetition(self, repetition):
		return self.remove_item('Repetitions', repetition.id)


class MetronomeSetupHandler(AbstractDatabaseHandler):

	def insert_metronome_setup(self, metronome):
		self._cur.execute("INSERT INTO MetronomeSetups(phrase_id, speed, meter, duration, increment) VALUES (%d, %d, %d, %d, %d)" % (metronome.phrase_id, metronome.speed, metronome.meter, metronome.duration, metronome.increment))
		self._con.commit()
		self._cur.execute("SELECT last_insert_rowid()")
		last_id = self._cur.fetchone()
		if last_id:
			return last_id[0]
		else:
			return None

	def _build_metronome_setup(self, data):
		ms = MetronomeSetup()
		ms.id = data['id']
		ms.phrase_id = data['phrase_id']
		ms.speed = data['speed']
		ms.meter = data['meter']
		ms.duration = data['duration']
		ms.increment = data['increment']
		return ms

	def get_metronome_setup_by_id(self, ms_id):
		data = self.get_item_by_id('MetronomeSetups', ms_id)
		if data:
			ms = self._build_metronome_setup(data)
			return ms
		else:
			return None

	def get_metronome_setups(self, orderby=None):
		rows = self.get_items('MetronomeSetups', orderby=orderby)
		result = []
		for row in rows:
			ms = self._build_metronome_setup(row)
			result.append(ms)
		return result

	def get_metronome_setups_by_phrase_id(self, phrase_id, orderby=None):
		rows = self.get_items_by_related_id('MetronomeSetups', 'phrase_id', phrase_id, orderby=orderby)
		result = []
		for row in rows:
			ms = self._build_metronome_setup(row)
			result.append(ms)
		return result

	def remove_metronome_setup(self, ms):
		return self.remove_item('MetronomeSetups', ms.id)

	def update_metronome_setup(self, ms):
		self._cur.execute("UPDATE MetronomeSetups SET "\
		"phrase_id=%d,speed=%d,meter=%d,duration=%d,increment=%d WHERE id=%d" % (ms.phrase_id,
                                                                                         ms.speed,
                                                                                         ms.meter,
                                                                                         ms.duration,
                                                                                         ms.increment,
                                                                                         ms.id))
		self._con.commit()
		return True

class DatabaseHandler(PhraseHandler, ScheduleHandler, RepetitionHandler, MetronomeSetupHandler):
	pass


class PrioritizedScheduleHandler(DatabaseHandler):

        def get_active_schedules(self, orderby=None):
                schedules = super(PrioritizedScheduleHandler, self).get_active_schedules()
                for schedule in schedules:
                        ri = libschedule.RepeatableItem()
                        phrase_id = schedule.get_phrase_id()
                        item_repetitions = self.get_repetitions_by_phrase_id(phrase_id, orderby='repetition_date')
                        print "Schedule", schedule.get_next_repetition()
                        for item_repetition in item_repetitions:
                            print "\t", item_repetition
                            lsr = libschedule.Repetition()
                            lsr.repetition_timestamp = float(item_repetition.get_date().strftime("%s"))
                            ri.repetitions.append(lsr)
                        ri.next_repetition_timestamp = float(schedule.get_next_repetition().strftime("%s"))
                        prio = ri.get_priority()
                        schedule.set_priority(prio)
                prioritized_list = sorted(schedules, key=lambda x: x.get_priority(), reverse=True)
                return prioritized_list
