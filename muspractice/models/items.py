import datetime
import time


class Repetition(object):

    def __init__(self):
        self.repetition_timestamp = None


class RepeatableItem(object):

    def __init__(self):
        self.repetitions = []
        self.next_repetition_timestamp = None
        
    def get_priority(self, repetition_time=None):
        """
        Calculate item repetition priority at the given time
        """
        if repetition_time is None:
            repetition_time = time.time()

        # non-scheduled items have no priority
        if self.next_repetition_timestamp is None:
            return None
        
        time_delta = repetition_time - self.next_repetition_timestamp
        # before the scheduled repetition date, the item will have no priority (None)
        if time_delta < 0:
            return None
        
        # if no repetitions made yet, the item will have priority 1.0
        if len(self.repetitions) == 0:
            return 100

        # if only one repetition has been made, priority will be 10
        if len(self.repetitions) == 1:
            return 75

        # if the item has no age, the item will have priority 0
        age = self.get_age()
        if age == 0:
            return 0

        age = age / float(86400)
        waiting = time_delta / float(86400)
        
        priority = (float(waiting) / age * 100.0) +  30.0 / len(self.repetitions)
        if priority < 0:
            return 0
        
        return priority

    def get_age(self):
        """Get item age

        Age is determined as the time difference between the first and the last repetition of the item
        """
        if len(self.repetitions) == 0:
            return None
        
        elif len(self.repetitions) == 1:
            last_repetition_timestamp = time.time()
            
        else:
            last_repetition_timestamp = self.repetitions[-1].repetition_timestamp
        age = last_repetition_timestamp - self.repetitions[0].repetition_timestamp
        return age
            
