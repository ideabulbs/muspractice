from .Serializable import *

class MetronomeSetup(Serializable):
    phrase_id = 0
    speed = 0
    meter = 0
    duration = 0
    increment = 0
    def __str__(self):
        if self.phrase_id:
            return "MetronomeSetup(phrase_id=%d, speed=%d, meter=%d, duration=%d, increment=%d)" % (self.phrase_id, self.speed, self.meter, self.duration, self.increment)
        else:
            return "MetronomeSetup(speed=%d, meter=%d, duration=%d, increment=%d)" % (self.speed, self.meter, self.duration, self.increment)

    def __eq__(self, other):
        phrase_id_match = self.phrase_id == other.phrase_id
        speed_match = self.speed == other.speed
        meter_match = self.meter == other.meter
        duration_match = self.duration == other.duration
        increment_match = self.increment == other.increment
        return phrase_id_match and speed_match and meter_match and duration_match and increment_match
