import time
import datetime

class Repetition(object):
	_id = None
	_phrase_id = None
	_date = None
	_speed = 0
	_pitch = 0
	_comment = ""
	_grade = 0
	def __str__(self):
		return "Repetition(phrase_id=%d; date=%s; speed=%d; pitch=%d; grade=%d)" % (self.get_phrase_id(), self.get_date(), self.get_speed(), self.get_pitch(), self.get_grade())
	def __eq__(self, other):
		phrase_id_match = self.get_phrase_id() == other.get_phrase_id()
		date_match = str(self.get_date()) == str(other.get_date())
		speed_match = self.get_speed() == other.get_speed()
		pitch_match = self.get_pitch() == other.get_pitch()
		grade_match = self.get_grade() == other.get_grade()
		return phrase_id_match and date_match and speed_match and pitch_match and grade_match
	def set_grade(self, grade):
		self._grade = grade
	def get_grade(self):
		return self._grade
	def set_comment(self, comment):
		self._comment = comment
	def get_comment(self):
		return self._comment
	def set_pitch(self, pitch):
		self._pitch = pitch
	def get_pitch(self):
		return self._pitch
	def set_speed(self, speed):
		self._speed = speed
	def get_speed(self):
		return self._speed
	def set_date(self, date):
		if isinstance(date, str) or isinstance(date, unicode):
			time_tuple = time.strptime(date,"%Y-%m-%d")[:3]
			date = datetime.date(time_tuple[0], time_tuple[1], time_tuple[2])
		self._date = date
	def get_date(self):
		return self._date
	def set_phrase_id(self, phrase_id):
		self._phrase_id = phrase_id
	def get_phrase_id(self):
		return self._phrase_id
	def set_id(self, new_id):
		self._id = new_id
	def get_id(self):
		return self._id
	
	
