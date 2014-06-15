import time
import subprocess
import threading
import sys
import os, signal


class Metronome:
	def __init__(self):
		self._duration = 0
		self._is_playing = False
		self._popen = None

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

		command = "klick -e %d" % (self._speed)
		self._is_playing = True
		if self._duration:
			sys.stderr.write("Starting metronome\n")
            # workaround to make klick start at the first attempt
			self._popen = subprocess.Popen(command.split(), shell=False)
			time.sleep(1)
			self._popen.terminate()
			time.sleep(1)
			self._popen = subprocess.Popen(command.split(), shell=False)
			self._metronome_wait = BackgroundWaitThread(self, self._duration, self._popen)
			self._metronome_wait.start()
			subprocess.Popen(['jack_connect', 'klick:out', 'system:playback_1'])
		else:
			self._popen = subprocess.Popen(command, shell=False)

	def is_playing(self):
		return self._is_playing

	def stop(self):
		if self._is_playing:
			self._metronome_wait.terminate()
			self._popen.kill()
			time.sleep(1)
			self._popen.terminate()
			self._is_playing = False

	def set_duration(self, duration):
		self._duration = duration

	def set_speed(self, speed):
		self._speed = speed

if __name__ == '__main__':
	m = Metronome()
	m.set_speed(130)
	m.set_duration(5)
	m.start()
	m.stop()
