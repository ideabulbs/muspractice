import subprocess
import os
from .test_functional import FunctionalBase

class TestTagWeights(FunctionalBase):

    def setup(self):
        FunctionalBase.setup(self)
        data = '''{
    "history_length": 400,
    "tag_weights": {
	"guitar vocal": 0.13,
	"guitar repertoire": 0.09,
	"guitar altpick": 0.09,
	"guitar scale": 0.09,
	"guitar sweep": 0.07,
	"guitar legato": 0.07,
	"guitar tapping": 0.07,
	"guitar chords": 0.07,
	"guitar rhythm": 0.09,
	"guitar phrasing": 0.09,
	"guitar improvisation": 0.06,
	"solfeggio": 0.08
    }
    
}
'''
        self.tag_weights_file = self.config.MUSIC_DIRECTORY + '/.muspractice_tag_weights'
        with open(self.tag_weights_file, 'w') as out:
            out.write(data)

    def teardown(self):
        if os.path.exists(self.tag_weights_file):
            os.unlink(self.tag_weights_file)
        FunctionalBase.teardown(self)

    def test_tag_weights(self):
        cmd = 'python muspractice/tag_weights -C %s -c %s' % (self.config_file, self.tag_weights_file)        
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        print(stdout)
        print(stderr)
        assert popen.returncode == 0
        assert len(stderr) == 0

        stdout = stdout.splitlines()
        assert len(stdout) == 2

        data_line = stdout[1].strip()
        tokens = data_line.decode('ascii').split('  ')
        assert len(tokens) == 3

        for token in tokens:
            category, reps = token.split(':')
            assert int(reps) <= 0

    def test_tag_weights_invalid_config(self):
        cmd = 'python muspractice/tag_weights -C %s -c .muspractice_tag_weights_non_existent' % (self.config_file)
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        print(stdout)
        print(stderr)
        assert popen.returncode == 1
        assert 'Could not find tag weight config' in stderr.decode('ascii')
        assert len(stdout) == 0
