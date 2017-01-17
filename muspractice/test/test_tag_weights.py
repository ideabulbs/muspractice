import subprocess

class TestTagWeights(object):

    def test_tag_weights(self):
        cmd = './tag_weights .muspractice_tag_weights'
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        assert popen.returncode == 0
        assert len(stderr) == 0

        stdout = stdout.splitlines()
        assert len(stdout) == 2

        data_line = stdout[1].strip()
        tokens = data_line.split('  ')
        assert len(tokens) == 3

        for token in tokens:
            category, reps = token.split(':')
            assert int(reps) <= 0

    def test_tag_weights_invalid_config(self):
        cmd = './tag_weights .muspractice_tag_weights_non_existent'
        popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        assert popen.returncode == 1
        assert 'Could not find tag weight config' in stderr
        assert len(stdout) == 0
