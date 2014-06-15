import subprocess
import os
from models.dbhandler import *
from helper import Helper

class FunctionalBase(Helper):

    dbfile = '/tmp/repetition_data.db'

    @classmethod
    def setup_class(cls):
        # clean up if file exists
        if os.path.exists(cls.dbfile):
                os.unlink(cls.dbfile)
        dbh = DatabaseHandler(cls.dbfile)
        dbh.init_database()

        phrase1 = cls._create_phrase()
        phrase2 = cls._create_phrase()
        phrase3 = cls._create_phrase()
        phrases = [phrase1, phrase2, phrase3]

        # import data to the database
        delta = 1
        for phrase in phrases:
            phrase_id = dbh.insert_phrase(phrase)

            # add a schedule to every added phrase
            schedule = Schedule()
            schedule.set_phrase_id(phrase_id)

            repetition_date = datetime.date.today() + datetime.timedelta(days=delta)
            delta += 1
            schedule.set_next_repetition(repetition_date)
            schedule_id = dbh.insert_schedule(schedule)

        schedules = dbh.get_schedules()
        assert len(schedules) > 0 and len(schedules) == len(phrases)

        # prevent editor from starting during automated tests
        if 'EDITOR' in os.environ:
            os.environ.pop('EDITOR', None)

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.dbfile):
            os.unlink(cls.dbfile)

    def run_program(self, keys):
        cmd = "./muspractice %s" % keys
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
                print stderr
                raise RuntimeError("pypractice ended with an unexpected error code: %d" % popen.returncode)
        return stdout, stderr

    def reschedule(self, phrase_id, grade):
        cmd = "./pypractice -d %s -r %s" % (self.dbfile, phrase_id)
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        popen.stdin.write(grade)
        stdout, stderr = popen.communicate()
        return stdout, stderr

    def get_phrase_list_length(self):
        keys = "-d %s -l" % self.dbfile
        stdout, stderr = self.run_program(keys)
        length = len(stdout.split(os.linesep))
        return length

    def get_todo_list_length(self):
        keys = "-d %s -t" % self.dbfile
        stdout, stderr = self.run_program(keys)
        length = len(stdout.split(os.linesep))
        return length

    def get_repetition_list_length(self):
        keys = "-d %s -R" % self.dbfile
        stdout, stderr = self.run_program(keys)
        length = len(stdout.split(os.linesep))
        return length

    def get_metronome_list_length(self):
        keys = "-d %s -M" % self.dbfile
        stdout, stderr = self.run_program(keys)
        length = len(stdout.split(os.linesep))
        return length


class TestFunctional(FunctionalBase):

    def test_list(self):
        keys = "-d %s -l" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert len(stderr) == 0

    def test_todo(self):
        keys = "-d %s -t" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert len(stderr) == 0

    def test_show_phrase(self):
        keys = "-d %s -s 1" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert len(stderr) == 0
        assert "File:" in stdout
        assert "From:" in stdout
        assert "To:" in stdout

    def test_deactivate_phrase(self):
        original_todo_list_length = self.get_todo_list_length()
        keys = "-d %s -x 2" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        current_list_length = self.get_todo_list_length()
        assert current_list_length == original_todo_list_length - 1

    def test_reactivate_phrase(self):
        original_todo_list_length = self.get_todo_list_length()
        phrase_id = "8"
        keys = "-d %s -x %s" % (self.dbfile, phrase_id)
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        deactivated_todo_list_length = self.get_todo_list_length()
        assert deactivated_todo_list_length == original_todo_list_length -1
        stdout, stderr = self.reschedule(phrase_id, "3")
        current_list_length = self.get_todo_list_length()
        assert current_list_length == deactivated_todo_list_length + 1

    def test_list_deactivated(self):
        keys = "-d %s -x 2" % self.dbfile
        stdout, stderr = self.run_program(keys)
        keys = "-d %s -X" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) > 1
        assert "2" in stdout
        assert "DEACTIVATED" in stdout

    def test_list_repetitions(self):
        # create repetition data: reschedule several phrases
        for item in ['5', '6', '7']:
                self.reschedule(item, '3')
        keys = "-d %s -R" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stdout.split(os.linesep)) >= 3

    def test_reschedule(self):
        stdout, stderr = self.reschedule("3", "3")
        assert "Next repetition" in stdout

    def test_delete(self):
        keys = "-d %s -D 4" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        assert "Phrase removed" in stdout

    def test_help(self):
        keys = "-h"
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        assert "Usage" in stdout

    def test_edit(self):
        original_phrase_list_length = self.get_phrase_list_length()
        keys = "-d %s -e 9" % self.dbfile
        stdout, stderr = self.run_program(keys)
        current_phrase_list_length = self.get_phrase_list_length()

        assert len(stderr) == 0
        assert original_phrase_list_length == current_phrase_list_length

    def test_create(self):
        original_phrase_list_length = self.get_phrase_list_length()
        original_todo_list_length = self.get_phrase_list_length()
        original_metronome_list_length = self.get_metronome_list_length()

        keys = "-d %s -c" % self.dbfile
        stdout, stderr = self.run_program(keys)

        current_phrase_list_length = self.get_phrase_list_length()
        current_todo_list_length = self.get_phrase_list_length()
        current_metronome_list_length = self.get_metronome_list_length()

        assert len(stderr) == 0
        assert current_phrase_list_length == original_phrase_list_length + 1
        assert current_todo_list_length == original_todo_list_length + 1
        assert current_metronome_list_length == original_metronome_list_length + 1

    def test_metronome_list(self):
        original_metronome_list_length = self.get_metronome_list_length()
        keys = "-d %s -c" % self.dbfile
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0
        current_metronome_list_length = self.get_metronome_list_length()
        assert current_metronome_list_length == original_metronome_list_length + 1

