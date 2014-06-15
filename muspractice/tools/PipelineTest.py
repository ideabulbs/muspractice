#!/usr/bin/python
from Pipeline import Pipeline
import gst
import time
TIME_FORMAT = gst.Format(gst.FORMAT_TIME)

class PipelineTest:
	def __init__(self):
		self._sink = gst.parse_bin_from_description('jackaudiosink', True)
		self._pipeline = Pipeline(self._sink)
		self._pipeline.reset()
		self._pipeline.set_file('file:///nas/music/rmusic/ME-work-song.mp3')
		pos = 0
		#pos = self._pipeline.pipe_time(pos)
		#self._pipeline.playbin.seek_simple(TIME_FORMAT, gst.SEEK_FLAG_FLUSH, pos)
		self._pipeline.play()
		time.sleep(10)


if __name__ == '__main__':
	pt = PipelineTest()

