import ConfigParser
from models.Phrase import *
from models.MetronomeSetup import *

class AbstractIniSerializator(object):

    def __init__(self, filename):
        self._filename = filename
        self._cfp = ConfigParser.RawConfigParser()

class MetronomeSetupIniserializator(AbstractIniSerializator):

    def set_metronome_setup(self, metronome_setup):
        cfp = self._cfp
        cfp.add_section('MetronomeSetup')
        cfp.set('MetronomeSetup', 'id', metronome_setup.id)
        cfp.set('MetronomeSetup', 'phrase_id', metronome_setup.phrase_id)
        cfp.set('MetronomeSetup', 'speed', metronome_setup.speed)
        cfp.set('MetronomeSetup', 'meter', metronome_setup.meter)
        cfp.set('MetronomeSetup', 'duration', metronome_setup.duration)
        cfp.set('MetronomeSetup', 'increment', metronome_setup.increment)

    def get_metronome_setup(self):
        cfp = self._cfp
        result = None
        if cfp.has_section('MetronomeSetup'):
            ms = MetronomeSetup()
            ms.id = cfp.getint('MetronomeSetup', 'id')
            ms.phrase_id = cfp.getint('MetronomeSetup', 'phrase_id')
            ms.speed = cfp.getint('MetronomeSetup', 'speed')
            ms.meter = cfp.getint('MetronomeSetup', 'meter')
            ms.duration = cfp.getint('MetronomeSetup', 'duration')
            ms.increment = cfp.getint('MetronomeSetup', 'increment')
            result = ms
        return result


class PhraseIniSerializator(AbstractIniSerializator):

	def set_phrase(self, phrase):
            cfp = self._cfp
            cfp.add_section('Phrase')
            cfp.set('Phrase', 'name', phrase.get_name())
            cfp.set('Phrase', 'filename', phrase.get_filename())
            cfp.set('Phrase', 'image', phrase.get_image())
            cfp.set('Phrase', 'tagline', phrase.get_tagline())
            cfp.set('Phrase', 'speed', phrase.get_speed())
            cfp.set('Phrase', 'pitch', phrase.get_pitch())
            cfp.set('Phrase', 'from_position', phrase.get_from_position())
            cfp.set('Phrase', 'to_position', phrase.get_to_position())
            cfp.set('Phrase', 'loop', phrase.get_loop())
            cfp.set('Phrase', 'comment', phrase.get_comment())

	def get_phrase(self):
            result = None
            cfp = self._cfp
            if cfp.has_section('Phrase'):
                name = cfp.get('Phrase', 'name')
                filename = cfp.get('Phrase', 'filename')
                filename = filename.replace("\\", "")
                image = cfp.get('Phrase', 'image')
                image = image.replace("\\", "")
                tagline = cfp.get('Phrase', 'tagline')
                speed = cfp.getint('Phrase', 'speed')
                pitch = cfp.getint('Phrase', 'pitch')
                from_position = cfp.getfloat('Phrase', 'from_position')
                to_position = cfp.getfloat('Phrase', 'to_position')
                loop = cfp.getboolean('Phrase', 'loop')
                comment = cfp.get('Phrase', 'comment')
                phrase = Phrase()
                phrase.id = self._phrase.id
                phrase.set_name(name)
                phrase.set_filename(filename)
                phrase.set_image(image)
                phrase.set_tagline(tagline)
                phrase.set_speed(speed)
                phrase.set_pitch(pitch)
                phrase.set_from_position(from_position)
                phrase.set_to_position(to_position)
                phrase.set_loop(loop)
                phrase.set_comment(comment)
                result = phrase
            return result


class IniSerializator(PhraseIniSerializator, MetronomeSetupIniserializator, AbstractIniSerializator):
    def __init__(self, filename, phrase=None, metronome_setup=None):
        AbstractIniSerializator.__init__(self, filename)
        self._phrase = phrase
        self._metronome_setup = metronome_setup

    def write(self):
        if self._phrase:
            self.set_phrase(self._phrase)
        if self._metronome_setup:
            self.set_metronome_setup(self._metronome_setup)

        with open(self._filename, 'wb') as config:
            self._cfp.write(config)
        return True

    def read(self):
        cfp = self._cfp
        cfp.read(self._filename)
        result = {}
        result['Phrase'] = None
        result['MetronomeSetup'] = None
        if cfp.has_section('Phrase'):
            phrase = self.get_phrase()
            if phrase:
                result['Phrase'] = phrase
        if cfp.has_section('MetronomeSetup'):
            ms = self.get_metronome_setup()
            if result['Phrase']:
                ms.phrase_id = result['Phrase'].id
                if ms:
                    result['MetronomeSetup'] = ms
        return result
