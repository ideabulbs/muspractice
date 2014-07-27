import sys
import datetime
import sqlite3
import libschedule
import app.models
from app.models import Phrase, Schedule, Repetition, MetronomeSetup
from django.utils.timezone import utc


class PhraseHandler(object):
    def insert_phrase(self, phrase):
        phrase.save()
        return phrase.id

    def remove_phrase(self, phrase):
        if phrase.id is not None:
            phrase.delete()
            return True
        else:
            return False

    def update_phrase(self, phrase):
        if phrase.id is not None:
            phrase.save()
            return True
        else:
            return False

    def get_phrase_by_id(self, phrase_id):
        try:
            phrase = Phrase.objects.get(id=phrase_id)
            return phrase
        except Phrase.DoesNotExist:
            return None

    def get_phrases(self, orderby=None):
        if not orderby:
            return Phrase.objects.all()
        else:
            return Phrase.objects.order_by(orderby)

    
class ScheduleHandler(object):
    def insert_schedule(self, schedule):
        schedule.save()
        return schedule.id

    def remove_schedule(self, schedule):
        if schedule.id is not None:
            schedule.delete()
            return True
        else:
            return False

    def get_schedule_by_id(self, schedule_id):
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            return schedule
        except Schedule.DoesNotExist:
            return None

    def get_schedules_by_phrase_id(self, phrase_id):
        schedules = Schedule.objects.filter(phrase__id=phrase_id)
        return schedules

    def get_schedules(self, orderby=None):
        if not orderby:
            return Schedule.objects.all()
        else:
            return Schedule.objects.order_by(orderby)

    def get_active_schedules(self):
        inactive_date = datetime.datetime(1970, 1, 1, 23, 59)
        inactive_date = inactive_date.replace(tzinfo=utc)
        return Schedule.objects.filter(next_repetition__gt=inactive_date)

    def get_inactive_schedules(self, orderby=None):
        inactive_date = datetime.datetime(1970, 1, 2, 0, 0)
        inactive_date = inactive_date.replace(tzinfo=utc)
        if not orderby:
            return Schedule.objects.filter(next_repetition__lt=inactive_date)
        else:
            return Schedule.objects.filter(next_repetition__lt=inactive_date).order_by(orderby)

    
class PrioritizedScheduleHandler(ScheduleHandler):

    def get_active_schedules(self, orderby=None):
        schedules = super(PrioritizedScheduleHandler, self).get_active_schedules()
        for schedule in schedules:
            ri = libschedule.RepeatableItem()
            phrase_id = schedule.phrase.id
            item_repetitions = self.get_repetitions_by_phrase_id(phrase_id, orderby='timestamp')
            for item_repetition in item_repetitions:
                lsr = libschedule.Repetition()
                lsr.repetition_timestamp = float(item_repetition.timestamp.strftime("%s"))
                ri.repetitions.append(lsr)
            ri.next_repetition_timestamp = float(schedule.next_repetition.strftime("%s"))
            prio = ri.get_priority()
            schedule.priority = prio
        prioritized_list = sorted(schedules, key=lambda x: x.priority, reverse=True)
        return prioritized_list

    
class RepetitionHandler(object):
    def insert_repetition(self, repetition):
        repetition.save()
        return repetition.id

    def get_repetition_by_id(self, repetition_id):
        try:
            repetition = Repetition.objects.get(id=repetition_id)
            return repetition
        except Repetition.DoesNotExist:
            return None

    def get_repetitions(self, orderby=None):
        if not orderby:
            return Repetition.objects.all()
        else:
            return Repetition.objects.order_by(orderby)

    def get_repetitions_by_phrase_id(self, phrase_id, orderby=None):
        if not orderby:
            repetitions = Repetition.objects.filter(phrase__id=phrase_id)
        else:
            repetitions = Repetition.objects.filter(phrase__id=phrase_id).order_by(orderby)
        result = []
        for r in repetitions:
            result.append(r)
        return result

    def remove_repetition(self, repetition):
        if repetition.id is not None:
            repetition.delete()
            return True
        else:
            return False
    
    
class MetronomeSetupHandler(object):
    def insert_metronome_setup(self, ms):
        ms.save()
        return ms.id

    def get_metronome_setup_by_id(self, ms_id):
        try:
            ms = MetronomeSetup.objects.get(id=ms_id)
            return ms
        except MetronomeSetup.DoesNotExist:
            return None

    def get_metronome_setups(self, orderby=None):
        if not orderby:
            return MetronomeSetup.objects.all()
        else:
            return MetronomeSetup.objects.order_by(orderby)

    def get_metronome_setups_by_phrase_id(self, phrase_id, orderby=None):
        if not orderby:
            mss = MetronomeSetup.objects.filter(phrase__id=phrase_id)
        else:
            mss = MetronomeSetup.objects.filter(phrase__id=phrase_id).order_by(orderby)
        return mss

    def remove_metronome_setup(self, ms):
        if ms.id is not None:
            ms.delete()
            return True
        else:
            return False

    def update_metronome_setup(self, ms):
        if ms.id is not None:
            ms.save()
            return True
        else:
            return False

        
class DatabaseHandler(PhraseHandler, PrioritizedScheduleHandler, RepetitionHandler, MetronomeSetupHandler):
	pass
