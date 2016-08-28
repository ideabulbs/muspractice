import time
import subprocess
import threading
import sys
import os, signal


class SightRead(object):

    duration = 0
    filename = None
        
    def __init__(self):
        self._is_playing = False
        self._popen = None
        
    def start(self):
            
        class BackgroundWaitThread(threading.Thread):
            def __init__(self, main_thread, wait_time, popen):
                super(self.__class__, self).__init__()
                self.setDaemon(True)
                self._wait_time = wait_time
                self._current_time = 0
                self._popen = popen
                self._main_thread = main_thread

            def wait(self):
                while self._current_time < self._wait_time:
                    time.sleep(1)
                    self._current_time += 1

            def terminate(self):
                self._current_time = self._wait_time

            def run(self):
                self.wait()
                self._main_thread.stop()
                                
        command = "xpaint %s" % (self.filename)
        self._is_playing = True
        if self.duration:
            self._popen = subprocess.Popen(command.split(), shell=False,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            self._wait_thread = BackgroundWaitThread(self, self.duration, self._popen)
            self._wait_thread.start()
        return True
    
    def is_playing(self):
        return self._is_playing

    def stop(self):
        if self._is_playing:
            self._wait_thread.terminate()
            self._popen.kill()
            self._is_playing = False
        return True
    
if __name__ == '__main__':
    sr = SightRead()
    sr.duration = 5
    sr.filename = 'data/goodmorning.png'
    sr.start()
    time.sleep(5)
    sr.stop()
