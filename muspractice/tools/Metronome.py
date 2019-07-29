import time
import subprocess
import threading
import sys
import os, signal


class Metronome(object):
    timeout = 10
    jack_port_name = 'klick:out'
    
    def __init__(self):
        self._duration = 0
        self._meter = 0
        self._is_playing = False
        self._popen = None
        self._jack_ports = []
        
    def wait_for_metronome_port(self, wait_open=True):
        for _ in range(self.timeout):
            popen = subprocess.Popen(['jack_lsp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = popen.communicate()
            if wait_open:
                if self.jack_port_name in stdout.decode('ascii'):
                    return True
            else:
                if not self.jack_port_name in stdout.decode('ascii'):
                    return True
            time.sleep(1)
        return False

    def start(self):
            
        class BackgroundWaitThread(threading.Thread):
            def __init__(self, metronome, wait_time, popen):
                super(self.__class__, self).__init__()
                self.setDaemon(True)
                self._wait_time = wait_time
                self._current_time = 0
                self._popen = popen
                self._metronome = metronome

            def wait(self):
                while self._current_time < self._wait_time:
                    time.sleep(1)
                    self._current_time += 1

            def terminate(self):
                self._current_time = self._wait_time

            def run(self):
                self.wait()
                self._metronome.stop()

        command = "klick"

        if os.environ.get('MUSPRACTICE_METRONOME_MUTE') != 'y':
            for port in self._jack_ports:
                command += " -p %s" % port
        if self._meter == 0:
            command += " -v 0.7 -e %d" % (self._speed)
        else:
            command += " %d/4 %d" % (self._meter, self._speed)
        
        self._is_playing = True
        if self._duration:
            self._popen = subprocess.Popen(command.split(), shell=False)
            self._metronome_wait = BackgroundWaitThread(self, self._duration, self._popen)
            self._metronome_wait.start()
            if not self.wait_for_metronome_port():
                return False
        else:
            self._popen = subprocess.Popen(command, shell=False)
        return True
    
    def is_playing(self):
        return self._is_playing

    def stop(self):
        if self._is_playing:
            self._metronome_wait.terminate()
            self._popen.kill()
            time.sleep(1)
            self._popen.terminate()
            self._is_playing = False
        for _ in range(self.timeout):
            if self.wait_for_metronome_port(wait_open=False):
                return True
        return False
    
    def set_duration(self, duration):
        self._duration = duration

    def set_speed(self, speed):
        self._speed = speed

    def set_meter(self, meter):
        self._meter = meter

    def set_jack_ports(self, ports):
        self._jack_ports = ports
        
if __name__ == '__main__':
    m = Metronome()
    m.set_speed(130)
    m.set_meter(3)
    m.set_duration(10)
    m.start()
    time.sleep(10)
    m.stop()
