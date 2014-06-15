import os
import tempfile

class Config:
	TEMPORARY_DIRECTORY = tempfile.mkdtemp()
	MUSIC_DIRECTORY = os.environ['MUSPRACTICE_MUSIC_DIRECTORY']
	AUDIOSINK = 'jackaudiosink'
