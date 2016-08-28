import subprocess
import os
import shutil
from models.dbhandler import *
from helper import Helper
from config.config import Config

class FunctionalBase(Helper):

    dbfile = '/tmp/repetition_data.db'
    
    @classmethod
    def _populate_db(cls, dbh, phrase_count):
        phrases = []
        for _ in range(phrase_count):
            phrase = cls._create_phrase()
            phrases.append(phrase)
        # import data to the database
        delta = 1
        for phrase in phrases:
            phrase_id = dbh.insert_phrase(phrase)

            # add a schedule to every added phrase
            schedule = Schedule()
            schedule.set_phrase_id(phrase_id)

            repetition_date = datetime.date.today() + datetime.timedelta(days=delta)
            delta -= 1
            schedule.set_next_repetition(repetition_date)
            schedule_id = dbh.insert_schedule(schedule)
        return True
        
    def setup(self):
        # clean up if file exists
        if os.path.exists(self.dbfile):
                os.unlink(self.dbfile)
        dbh = DatabaseHandler(self.dbfile)
        dbh.init_database()

        self.phrase_count = 10
        self._populate_db(dbh, self.phrase_count)
        
        schedules = dbh.get_schedules()
        assert len(schedules) > 0 and len(schedules) == self.phrase_count

        # prevent editor from starting during automated tests
        if 'EDITOR' in os.environ:
            os.environ.pop('EDITOR', None)

    def teardown(self):
        if os.path.exists(self.dbfile):
           os.unlink(self.dbfile)
            
    def run_program(self, keys):
        cmd = "./muspractice %s" % keys
        popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
                print stderr
                raise RuntimeError("muspractice ended with an unexpected error code: %d" % popen.returncode)
        return stdout, stderr

    def reschedule(self, phrase_id, grade):
        cmd = "./muspractice -d %s -r %s" % (self.dbfile, phrase_id)
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        popen.stdin.write(grade)
        stdout, stderr = popen.communicate()
        return stdout, stderr

    def get_phrase_list_length(self):
        keys = "-d %s -l" % self.dbfile
        stdout, stderr = self.run_program(keys)
        length = len(stdout.strip().split(os.linesep))
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

    remove_files = []
    
    def teardown(self):
        FunctionalBase.teardown(self)
        if self.remove_files:
            for f in self.remove_files:
                if os.path.exists(f):
                    os.unlink(f)
            del self.remove_files[:]
    
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
        phrase_id = "9"
        keys = "-d %s -x %s" % (self.dbfile, phrase_id)
        stdout, stderr = self.run_program(keys)
        assert len(stderr) == 0

        keys = "-d %s -X" % self.dbfile
        stdout, stderr = self.run_program(keys)
        initial_deactivated_list_length = len(stdout.split(os.linesep))
        stdout, stderr = self.reschedule(phrase_id, "3")
        assert not stderr
        stdout, stderr = self.run_program(keys)
        current_deactivated_list_length = len(stdout.split(os.linesep))
        assert current_deactivated_list_length == initial_deactivated_list_length - 1
        

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

    def test_database_path(self):
        alternate_db_file = '/tmp/altdb.db'
        self.remove_files.append(alternate_db_file)
        alt_dbh = DatabaseHandler(alternate_db_file)
        alt_dbh.init_database()
        
        # insert two more phrases than in the main database created in setup_class:
        phrase_count = self.get_phrase_list_length() + 2
        if not self._populate_db(alt_dbh, phrase_count):
            raise RuntimeError("Could not populate test database: %s" % alternate_db_file)
        
        phrases = []
        for _ in range(phrase_count):
            phrase = self._create_phrase()
            phrases.append(phrase)
        keys = '-l -d %s' % alternate_db_file
        stdout, stderr = self.run_program(keys)
        current_phrase_list_length = len(stdout.strip().split(os.linesep))
        assert current_phrase_list_length == phrase_count

        
class TestBulkAdd(FunctionalBase):

    remove_files = []
    remove_directories = []
    
    def teardown(self):
        FunctionalBase.teardown(self)
        if self.remove_files:
            for f in self.remove_files:
                if os.path.exists(f):
                    os.unlink(f)
            del self.remove_files[:]
            
        if self.remove_directories:
            for d in self.remove_directories:
                if os.path.exists(d):
                    shutil.rmtree(d)
            del self.remove_directories[:]

    def test_bulk_add(self):
        """
        Add 3 files in bulk mode and verify that they are added
        """
        config = Config('.muspracticerc')
        rel_dir = 'testdir'
        full_path = '%s%s' % (config.MUSIC_DIRECTORY, rel_dir)
        self.remove_directories.append(full_path)
        if not os.path.exists(full_path):
            os.mkdir(full_path)            
        cmds = ["touch %s/001.png" % full_path,
                "touch %s/002.png" % full_path,
                "touch %s/003.png" % full_path]
        for cmd in cmds:
            popen = subprocess.Popen(cmd, shell=True)
            popen.communicate()
            if popen.returncode != 0:
                raise RuntimeError('Could not execute command %s' % cmd)
        initial_phrase_count = self.get_phrase_list_length()
        keys = '-d %s -b %s --tagline "test tags"' % (self.dbfile, rel_dir)
        stdout, stderr = self.run_program(keys)
        current_phrase_count = self.get_phrase_list_length()
        assert current_phrase_count == initial_phrase_count + 3
        
