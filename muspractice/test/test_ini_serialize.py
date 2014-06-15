import sqlite3
from models.dbhandler import DatabaseHandler
from models.Schedule import Schedule
from models.Scheduler import Scheduler
from models.Repetition import Repetition
from models.MetronomeSetup import *
from config.config import Config
from helper import Helper
import os
import datetime
from models.IniSerializator import *

class TestIniSerialize(Helper):

    dbfile = 'test.db'
    inifile = 'test.ini'

    def teardown(self):
        if os.path.exists(self.dbfile):
            os.unlink(self.dbfile)
        if os.path.exists(self.inifile):
            os.unlink(self.inifile)

    def test_ini_serialize(self):
        dbh = DatabaseHandler(self.dbfile)
        dbh.init_database()

        phrase = self._create_phrase()
        phrase_id = dbh.insert_phrase(phrase)
        phrase.id = phrase_id

        ms = MetronomeSetup()
        ms.phrase_id = phrase_id
        ms.speed = 100
        ms.meter = 4
        ms.duration = 300
        ms.increment = 8

        ms.id = dbh.insert_metronome_setup(ms)

        inis = IniSerializator(self.inifile, phrase=phrase, metronome_setup=ms)
        write_result = inis.write()
        assert write_result

        edited = inis.read()
        assert edited['Phrase'] != None
        assert edited['MetronomeSetup'] != None
        assert edited['Phrase'] == phrase
        assert edited['MetronomeSetup'] == ms

