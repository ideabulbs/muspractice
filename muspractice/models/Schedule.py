import datetime
import time
from .Serializable import *

class Schedule(Serializable):

    _phrase_id = None
    _next_repetition = None
    _speed = 0
    _pitch = 0
    _comment = ""
    _priority = 0
    
    def set_priority(self, priority):
        self._priority = priority

    def get_priority(self):
        return self._priority

    def __init__(self):
        self._next_repetition = datetime.date.today()
    
    def __eq__(self, other):
        phrase_match = self.get_phrase_id() == other.get_phrase_id()
        next_repetition_match = str(self.get_next_repetition()) == str(other.get_next_repetition())
        speed_match = self.get_speed() == other.get_speed()
        pitch_match = self.get_pitch() == other.get_pitch()
        comment_match = self.get_comment() == other.get_comment()
        return phrase_match and next_repetition_match and speed_match and pitch_match and comment_match

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

    def set_next_repetition(self, date):
        if isinstance(date, str) or isinstance(date, str):
            time_tuple = time.strptime(date,"%Y-%m-%d")[:3]
            date = datetime.date(time_tuple[0], time_tuple[1], time_tuple[2])
        self._next_repetition = date

    def get_next_repetition(self):
        return self._next_repetition

    def set_phrase_id(self, new_id):
        self._phrase_id = new_id

    def get_phrase_id(self):
        return self._phrase_id
