import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import re
import os


GObject.threads_init()
Gst.init(None)

TIME_FORMAT = Gst.Format(Gst.Format.TIME)

class PipelineBase(Gst.Pipeline):

    def __init__(self, sink):
        Gst.Pipeline.__init__(self)
        self.playbin = Gst.ElementFactory.make("playbin")
        self.add(self.playbin)

        bin = Gst.Bin()
        self.speedchanger = Gst.ElementFactory.make("pitch")
        if self.speedchanger is None:
            print("You need to install the Gstreamer soundtouch elements for "
                  "play it slowly to. They are part of Gstreamer-plugins-bad. Consult the "
                  "README if you need more information.")
            raise SystemExit()

        bin.add(self.speedchanger)

        self.audiosink = Gst.parse_launch(sink)
        bin.add(self.audiosink)
        convert = Gst.ElementFactory.make("audioconvert")
        bin.add(convert)
        self.speedchanger.link(convert)
        convert.link(self.audiosink)
        sink_pad = Gst.GhostPad.new("sink", self.speedchanger.get_static_pad("sink"))
        bin.add_pad(sink_pad)
        self.playbin.set_property("audio-sink", bin)

        self.eos = lambda: None

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MESSAGE_EOS:
            self.eos()
        elif t == Gst.MESSAGE_ERROR:
            print("Gstreamer error: %s - %s" % message.parse_error())

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
        pipeline = Gst.Pipeline()

        playbin = Gst.ElementFactory.make("playbin")
        pipeline.add(playbin)
        playbin.set_property("uri", self.playbin.get_property("uri"))

        bin = Gst.Bin()

        speedchanger = Gst.ElementFactory.make("pitch")
        speedchanger.set_property("tempo", self.speedchanger.get_property("tempo"))
        speedchanger.set_property("pitch", self.speedchanger.get_property("pitch"))
        bin.add(speedchanger)

        audioconvert = Gst.ElementFactory.make("audioconvert")
        bin.add(audioconvert)

        encoder = Gst.ElementFactory.make("wavenc")
        bin.add(encoder)

        filesink = Gst.ElementFactory.make("filesink")
        bin.add(filesink)
        filesink.set_property("location", uri)

        speedchanger.link(audioconvert)
        audioconvert.link(encoder)
        encoder.link(filesink)

        sink_pad = Gst.GhostPad.new("sink", speedchanger.get_static_pad("sink"))
        bin.add_pad(sink_pad)
        playbin.set_property("audio-sink", bin)

        pipeline.set_state(Gst.State.PLAYING)

        return (pipeline, playbin)

    def set_file(self, uri):
        self.playbin.set_property("uri", uri)

    def play(self):
        self.set_state(Gst.State.PLAYING)

    def pause(self):
        self.set_state(Gst.State.PAUSED)

    def reset(self):
        self.set_state(Gst.State.READY)


class Pipeline(PipelineBase):

    def __init__(self, sink):
        PipelineBase.__init__(self, sink)
        self._paused = True
        self._loop = False
        self._from_position = 0
        self._to_position = 0

    def get_duration(self):
        try:
            _, duration = self.playbin.query_duration(TIME_FORMAT)
            duration = self.song_time(duration)
            return duration
        except Exception as e:
            sys.stderr.write("GST QUERY ERROR: %s\n" % e)
            return None

    def get_position(self):
        try:
            _, position = self.playbin.query_position(TIME_FORMAT)
            position = self.song_time(position)
            return position
        except Exception:
            return None

    def get_from_position(self):
        return self._from_position
    
    def set_from_position(self, position):
        self._from_position = position

    def get_to_position(self):
        return self._to_position

    def set_to_position(self, position):
        self._to_position = position

    def set_loop(self, loop):
        self._loop = loop

    def get_loop(self):
        return self._loop

    def play(self):
        PipelineBase.play(self)
        self._paused = False

    def pause(self):
        PipelineBase.pause(self)
        self._paused = True

    def is_paused(self):
        return self._paused

    def is_playing(self):
        return not self.is_paused()

    def seek_simple(self, pos=0):
        pos = self.pipe_time(pos)
        self.playbin.seek_simple(TIME_FORMAT, Gst.SeekFlags.FLUSH, pos or 0)

if __name__ == "__main__":
    import time
    pl = Pipeline('jackaudiosink')
    pl.reset()
    path = 'file://%stest/data/music.mp3' % os.getcwd()
    path = 'file:///home/user/shared/repmusic/rock/burn.mp3'
    print("Playing", path)
    pl.set_file(path)
    pl.play()
    time.sleep(2)
    print('Position', pl.get_position())
    print('Playing for 2 seconds', pl.is_playing())
    time.sleep(2)
    print('Position', pl.get_position())
    print('pausing for 2 seconds')
    pl.pause()
    time.sleep(2)
    print('Position', pl.get_position())
    pl.play()
    time.sleep(10)
    print('Position', pl.get_position())
    pl.pause()
