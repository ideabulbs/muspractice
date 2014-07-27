from app.models import Schedule, Repetition
import random
import datetime
from django.utils.timezone import utc


class Scheduler(object):

    def _get_new_interval(self, previous_interval, current_grade):

        interval = 0

        if current_grade == 3:
            interval_factor = 1.3
        elif current_grade == 4:
            interval_factor = 1.4
        elif current_grade == 5:
            interval_factor = 1.5
        else:
            interval_factor = 1.2
            
        if previous_interval == 0:
            new_interval = random.randint(1,2)
        elif previous_interval == 1:
            new_interval = random.randint(2,3)
        elif previous_interval == 2:
            new_interval = random.randint(3,4)
        elif previous_interval == 3:
            new_interval = random.randint(4,5)
        elif previous_interval == 4:
            new_interval = random.randint(5,7)
        elif previous_interval == 5:
            new_interval = random.randint(7,9)
        elif previous_interval == 6:
            new_interval = random.randint(8,10)
        elif previous_interval == 7:
            new_interval = random.randint(10,12)
        elif previous_interval == 8:
            new_interval = random.randint(11,13)
        elif previous_interval == 9:
            new_interval = random.randint(13,16)
        elif previous_interval > 9:
            new_interval = int(previous_interval * interval_factor)

        if current_grade == 0:
            new_interval = random.randint(1,2)
        elif current_grade == 1:
            new_interval = random.randint(2,3)
        elif current_grade == 2:
            new_interval = random.randint(3,4)
            
        return new_interval
            
    def get_new_schedule(self, phrase, grade, repetition_list=None):
        """
        @param repetition_list: sorted repetition list (earliest rep first)
        @type repetition_list: list of models.Repetition
        @return: new schedule
        @rtype: models.Schedule
        """
        schedule = Schedule()
        schedule.phrase = phrase
        new_interval = 1
        if repetition_list and len(repetition_list) > 1:
            rep1 = repetition_list[-2]
            rep2 = repetition_list[-1]
            date1 = rep1.timestamp
            date2 = rep2.timestamp
            delta = date2 - date1
            new_interval = self._get_new_interval(delta.days, grade)
        elif repetition_list:
            new_interval = self._get_new_interval(1, grade)
        else:
            new_interval = self._get_new_interval(0, grade)
        next_rep = datetime.datetime.utcnow() + datetime.timedelta(days=new_interval)
        next_rep = next_rep.replace(tzinfo=utc)
        schedule.next_repetition = next_rep
        return schedule
