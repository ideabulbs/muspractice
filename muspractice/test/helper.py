#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program description
@author: Andrei Matveyeu
@organization: ideabulbs.com
@license: GNU GPL
@contact: andrei@ideabulbs.com
"""
from models.Schedule import Schedule
from models.Phrase import Phrase
import time


class Helper(object):

    @classmethod
    def _create_phrase(cls):
        phrase = Phrase()
        unique_token = "%.6f" % time.time()
        phrase.set_name('test_phrase_%s' % unique_token)
        phrase.set_filename("%s.mp3" % unique_token)
        phrase.set_image("%s.png" % unique_token)
        phrase.set_tagline("tag1 tag2 tag3")
        phrase.set_from_position(10.0)
        phrase.set_to_position(20.0)
        phrase.set_loop(True)
        phrase.set_speed(80)
        phrase.set_pitch(2)
        phrase.set_comment("Test comment %s" % unique_token)
        phrase.set_metronome_id(None)
        return phrase

    @classmethod
    def _create_schedule(cls):
        schedule = Schedule()
        unique_token = "%.6f" % time.time()
        schedule.set_priority(1)
        schedule.set_comment("Test comment for schedule %s" % unique_token)
        schedule.set_pitch(2)
        schedule.set_speed(80)
        schedule.set_next_repetition('2020-12-12')
        return schedule
