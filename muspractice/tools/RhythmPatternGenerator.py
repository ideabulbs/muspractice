import random
import subprocess

class RhythmPatternGenerator(object):
	def __init__(self):
		self._generated = False
		self._midge_filename = '/tmp/rhythm.mg'

	def get_rhythm_pattern(self, beats, division, note, rest):
		notes=[]
		for a in range(0, note):
			notes.append("c3")
		for a in range(0, rest):
			notes.append("r")
		pattern="/l16/"
		for a in range(0, beats*division):
			pattern=pattern + random.choice(notes) + " "
		return pattern

	def set_midi_filename(self, filename):
		self._midi_filename = filename

	def set_midge_filename(self, filename):
		self._midge_filename = filename

	def set_random_tempo(self):
		self._tempo = random.randint(80, 125)

	def set_random_meter(self):
		self._meter = random.randint(3,6)

	def set_tempo(self, tempo):
		self._tempo = tempo

	def set_duration(self, duration):
		self._duration = duration

	def set_meter(self, meter):
		self._meter = meter

	def generate(self):
		pattern=self.get_rhythm_pattern(self._meter, self._meter,  1, 1)
		beat_duration = 60.0 / self._tempo
		measure_duration = beat_duration * self._meter
		beats = int(self._duration / beat_duration)
		repetitions = int (self._duration / measure_duration)
		out_string = """
		@head {
		$tempo """ + str(self._tempo) +  """
		$time_sig """ + str(self._meter) + """/4
		}
		@body {
        %define bass { """ +  pattern + """}
		@channel 10 "drums" {
						$length 4
						$volume 70
								/r""" + str(beats) + """/f+3
							}

			@channel 10 "drums" {
						$length """ + str(self._meter) + """:4
								/r""" + str(repetitions) + """/d+3
							}

		"""
		out_string += """

				@channel 10 "drums" {
						$volume 127
						$bank 1
								%repeat """ + str(repetitions) + """ { ~bass }
							}

							} # end body

		"""
		out = open(self._midge_filename, "w")
		out.write(out_string)
		out.close()
		midge_result = subprocess.call(['midge', '/tmp/rhythm.mg', '-o', '/tmp/rhythm.mid'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if midge_result == 0:
			self._generated = True

	def get_midi_filename(self):
		if self._generated:
			return self._midi_filename
		else:
			return None

if __name__ == "__main__":
	rg = RhythmPatternGenerator()
	rg.set_midi_filename('/tmp/rhythm.mid')
	rg.set_random_tempo()
	rg.set_duration(300)
	rg.set_meter(8)
	rg.generate()

