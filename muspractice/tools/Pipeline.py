import sys
#import pygst
import gst
import mad
#pygst.require('0.10')
import re

argv = sys.argv
# work around gstreamer parsing sys.argv!
sys.argv = []
sys.argv = argv

#from playitslowly import mygtk
TIME_FORMAT = gst.Format(gst.FORMAT_TIME)

_ = lambda x: x

class Pipeline(gst.Pipeline):
	def __init__(self, sink):
		gst.Pipeline.__init__(self)
		self.playbin = gst.element_factory_make("playbin")
		self.add(self.playbin)

		bin = gst.Bin("speed-bin")
		try:
			self.speedchanger = gst.element_factory_make("pitch")
		except gst.ElementNotFoundError:
			mygtk.show_error(_(u"You need to install the gstreamer soundtouch elements for "
					"play it slowly to. They are part of gstreamer-plugins-bad. Consult the "
					"README if you need more information.")).run()
			raise SystemExit()

		bin.add(self.speedchanger)

		self.audiosink = sink

		bin.add(self.audiosink)
		convert = gst.element_factory_make("audioconvert")
		bin.add(convert)
		gst.element_link_many(self.speedchanger, convert)
		gst.element_link_many(convert, self.audiosink)
		sink_pad = gst.GhostPad("sink", self.speedchanger.get_pad("sink"))
		bin.add_pad(sink_pad)
		self.playbin.set_property("audio-sink", bin)
		bus = self.playbin.get_bus()
		bus.add_signal_watch()
		bus.connect("message", self.on_message)
		self.eos = lambda: None
		self._paused = True
		self._loop = False
		self._from_position = 0
		self._to_position = 0

	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.eos()
		elif t == gst.MESSAGE_ERROR:
			mygtk.show_error("gstreamer error: %s - %s" % message.parse_error())

	def get_duration(self):
		try:
			duration, fmt = self.playbin.query_duration(TIME_FORMAT, None)
		except gst.QueryError as e:
			sys.stderr.write("GST QUERY ERROR: %s\n" % e)
			return None
		duration = self.song_time(duration)
		return duration

	def get_position(self):
		try:
			position, fmt = self.playbin.query_position(TIME_FORMAT, None)
		except gst.QueryError:
			return None
		position = self.song_time(position)
		return position

	def set_volume(self, volume):
		self.playbin.set_property("volume", volume)

	def set_speed(self, speed):
		self.speedchanger.set_property("tempo", speed)

	def get_speed(self):
		return self.speedchanger.get_property("tempo")

	def pipe_time(self, t):
		"""convert from song position to pipeline time"""
		return t/self.get_speed()*1000000000

	def song_time(self, t):
		"""convert from pipetime time to song position"""
		return t*self.get_speed()/1000000000

	def set_pitch(self, pitch):
		self.speedchanger.set_property("pitch", pitch)

	def save_file(self, uri):
		pipeline = gst.Pipeline()

		playbin = gst.element_factory_make("playbin")
		pipeline.add(playbin)
		playbin.set_property("uri", self.playbin.get_property("uri"))

		bin = gst.Bin("speed-bin")

		speedchanger = gst.element_factory_make("pitch")
		speedchanger.set_property("tempo", self.speedchanger.get_property("tempo"))
		speedchanger.set_property("pitch", self.speedchanger.get_property("pitch"))
		bin.add(speedchanger)

		audioconvert = gst.element_factory_make("audioconvert")
		bin.add(audioconvert)

		encoder = gst.element_factory_make("wavenc")
		bin.add(encoder)

		filesink = gst.element_factory_make("filesink")
		bin.add(filesink)
		filesink.set_property("location", uri)

		gst.element_link_many(speedchanger, audioconvert)
		gst.element_link_many(audioconvert, encoder)
		gst.element_link_many(encoder, filesink)

		sink_pad = gst.GhostPad("sink", speedchanger.get_pad("sink"))
		bin.add_pad(sink_pad)
		playbin.set_property("audio-sink", bin)

		bus = playbin.get_bus()
		bus.add_signal_watch()
		bus.connect("message", self.on_message)

		pipeline.set_state(gst.STATE_PLAYING)

		return (pipeline, playbin)

	def set_file(self, uri):
		self.playbin.set_property("uri", uri)

	def get_file(self):
		filename = self.playbin.get_property("uri")
		filename = re.sub('file://', '', filename)
		return filename

	def play(self):
		self._paused = False
		self.set_state(gst.STATE_PLAYING)

	def set_from_position(self, position):
		self._from_position = position

	def get_from_position(self):
		return self._from_position

	def set_to_position(self, position):
		self._to_position = position

	def get_to_position(self):
		return self._to_position

	def seek(self, position):
		pos = self.pipe_time(position)
		self.playbin.seek_simple(TIME_FORMAT, gst.SEEK_FLAG_FLUSH, pos)

	def pause(self):
		self._paused = True
		self.set_state(gst.STATE_PAUSED)

	def set_loop(self, loop):
		self._loop = loop

	def get_loop(self):
		return self._loop
	def is_paused(self):
		return self._paused

	def is_playing(self):
		if not self.is_paused():
			return True
		else:
			return False

	def reset(self):
		self.set_state(gst.STATE_READY)


