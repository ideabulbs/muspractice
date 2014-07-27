import ConfigParser
from app.models import Phrase, MetronomeSetup, Tag


class AbstractIniSerializator(object):

    def __init__(self, filename):
        self._filename = filename
        self._cfp = ConfigParser.RawConfigParser()

class MetronomeSetupIniserializator(AbstractIniSerializator):

    def set_metronome_setup(self, metronome_setup):
        cfp = self._cfp
        cfp.add_section('MetronomeSetup')
        cfp.set('MetronomeSetup', 'id', metronome_setup.id)
        cfp.set('MetronomeSetup', 'phrase_id', metronome_setup.phrase.id)
        cfp.set('MetronomeSetup', 'speed', metronome_setup.speed)
        cfp.set('MetronomeSetup', 'speed_increment', metronome_setup.speed)
        cfp.set('MetronomeSetup', 'meter', metronome_setup.meter)
        cfp.set('MetronomeSetup', 'duration', metronome_setup.duration)
        cfp.set('MetronomeSetup', 'volume', metronome_setup.volume)


    def get_metronome_setup(self):
        cfp = self._cfp
        result = None
        if cfp.has_section('MetronomeSetup'):
            ms = MetronomeSetup()
            ms.id = cfp.getint('MetronomeSetup', 'id')
            ms.phrase_id = cfp.getint('MetronomeSetup', 'phrase_id')
            ms.speed = cfp.getfloat('MetronomeSetup', 'speed')
            ms.speed_increment = cfp.getfloat('MetronomeSetup', 'speed_increment')
            ms.meter = cfp.getint('MetronomeSetup', 'meter')
            ms.duration = cfp.getfloat('MetronomeSetup', 'duration')
            ms.volume = cfp.getfloat('MetronomeSetup', 'volume')
            result = ms
        return result


class PhraseIniSerializator(AbstractIniSerializator):

	def set_phrase(self, phrase):
            cfp = self._cfp
            cfp.add_section('Phrase')
            cfp.set('Phrase', 'name', phrase.name)
            cfp.set('Phrase', 'filename', phrase.get_filename())
            cfp.set('Phrase', 'image', phrase.image)
            cfp.set('Phrase', 'tagline', phrase.get_tagline())
            cfp.set('Phrase', 'speed', phrase.speed)
            cfp.set('Phrase', 'speed_increment', phrase.speed_increment)
            cfp.set('Phrase', 'pitch', phrase.pitch)
            cfp.set('Phrase', 'volume', phrase.volume)
            cfp.set('Phrase', 'from_position', phrase.from_position)
            cfp.set('Phrase', 'to_position', phrase.to_position)
            cfp.set('Phrase', 'loop', phrase.loop)
            cfp.set('Phrase', 'comment', phrase.comment)

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
                speed = cfp.getfloat('Phrase', 'speed')
                speed_increment = cfp.getfloat('Phrase', 'speed_increment')
                volume = cfp.getfloat('Phrase', 'volume')
                pitch = cfp.getfloat('Phrase', 'pitch')
                from_position = cfp.getfloat('Phrase', 'from_position')
                to_position = cfp.getfloat('Phrase', 'to_position')
                loop = cfp.getboolean('Phrase', 'loop')
                comment = cfp.get('Phrase', 'comment')
                phrase = Phrase()
                phrase.id = self._phrase.id
                phrase.name = name
                phrase.filename = filename
                phrase.image = image
                phrase.speed = speed
                phrase.speed_increment = speed_increment
                phrase.volume = volume
                phrase.pitch = pitch
                phrase.from_position = from_position
                phrase.to_position = to_position
                phrase.loop = loop
                phrase.comment = comment
                phrase.save()
                phrase.set_tagline(tagline)
                phrase.save()
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
