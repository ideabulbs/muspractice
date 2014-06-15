#!/usr/bin/python
import mad

mf = mad.MadFile('test/data/music.mp3')
mf = mad.MadFile('/tmp/audiofile.mp3')
print mf.total_time() / 1000.0
