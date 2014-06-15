import os
from Serializable import *

class Phrase(Serializable):

    _filename = ""
    _image = ""
    _tagline = ""
    _from_position = 0
    _to_position = 0
    _loop = False
    _speed = 100
    _pitch = 0
    _comment = ""
    _name = ""
    _metronome_id = 0

    def __eq__(self, other):
        names_match = self.get_name() == other.get_name()
        files_match = self.get_filename() == other.get_filename()
        tagline_match = self.get_tagline() == other.get_tagline()
        from_match = self.get_from_position() == other.get_from_position()
        to_match = self.get_to_position() == other.get_to_position()
        loop_match = self.get_loop() == other.get_loop()
        speed_match = self.get_speed() == other.get_speed()
        pitch_match = self.get_pitch() == other.get_pitch()
        image_match = self.get_image() == other.get_image()
        comment_match = self.get_comment() == other.get_comment()
        metronome_parameters_match = self.get_metronome_id() == other.get_metronome_id()
        if self.get_metronome_id() is None or other.get_metronome_id() is None:
            metronome_parameters_match = True
        return names_match\
               and files_match \
               and tagline_match \
               and from_match \
               and to_match \
               and loop_match \
               and speed_match \
               and pitch_match \
               and comment_match \
               and image_match \
               and metronome_parameters_match

    def set_name(self, name):
            self._name = name

    def get_name(self):
            return self._name

    def set_filename(self, filename):
            self._filename = filename

    def get_filename(self, path=True):
            if not path:
                    filename = self._filename.split(os.sep)[-1]
                    return filename
            else:
                    return self._filename

    def set_image(self, image):
            self._image = image

    def get_image(self):
            return self._image

    def set_tagline(self, tagline):
            self._tagline = tagline

    def get_tagline(self):
            return self._tagline

    def set_from_position(self, from_position):
            self._from_position = from_position

    def get_from_position(self):
            return self._from_position

    def set_to_position(self, to_position):
            self._to_position = to_position

    def get_to_position(self):
            return self._to_position

    def set_loop(self, loop):
            self._loop = loop

    def get_loop(self):
            return self._loop

    def set_speed(self, speed):
            self._speed = speed

    def get_speed(self):
            return self._speed

    def set_pitch(self, pitch):
            self._pitch = pitch

    def get_pitch(self):
            return self._pitch

    def set_comment(self, comment):
            self._comment = comment

    def get_comment(self):
            return self._comment

    def get_short_description(self):
            if self._comment:
                    lines = self._comment.split(os.linesep)
                    return lines[0].strip()
            else:
                    return ""

    def get_metronome_id(self):
            return self._metronome_id

    def set_metronome_id(self, new_id):
            self._metronome_id = new_id
