import time
import os
import subprocess
from ..tools.Pipeline import Pipeline


class TestPipeline(object):

    mp3_file = '%s/muspractice/test/data/music.mp3' % os.getcwd()
    sink = 'jackaudiosink'

    def test_gstreamer_decoder(self):
        cmd = 'gst-inspect-1.0'
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, _ = popen.communicate()
        # check if fluendo gstreamer plugin is installed
        print(stdout)
        assert 'flump3dec:' in stdout.decode('ascii')
    
    def test_pipeline_play(self):
        pl = Pipeline(self.sink)
        pos1 = pl.get_position()
        assert pos1 == 0
        
        if not os.path.exists(self.mp3_file):
            raise RuntimeError('Cannot find test data file: %s' % self.mp3_file)       
        pl.set_file('file://%s' % self.mp3_file)
        pl.play()
        time.sleep(2)

        assert pl.is_playing()

        pos2 = pl.get_position()
        assert pos2 > pos1 and pos2 > 1.0

    def test_pipeline_pause(self):
        pl = Pipeline(self.sink)
        if not os.path.exists(self.mp3_file):
            raise RuntimeError('Cannot find test data file: %s' % self.mp3_file)
        pl.set_file('file://%s' % self.mp3_file)
        pl.play()
        
        time.sleep(2)
        assert pl.get_position() > 0
        pl.pause()
        
        assert not pl.is_playing()
        
        pos1 = pl.get_position()
        time.sleep(2)
        pos2 = pl.get_position()
        assert pos1 == pos2
        
        pl.play()
        time.sleep(1)
        assert pl.is_playing()
        
        pos3 = pl.get_position()
        assert pos3 > pos2
