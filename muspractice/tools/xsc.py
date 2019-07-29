import os
import math
from mutagen.mp3 import MP3

class SectionMarker(object):
    def __init__(self):
        self.name = ""
        self.pos = 0.0

class Section(object):

    def __init__(self):
        self.start_pos = 0
        self.end_pos = 0
        self.name = ""
        self.source_filename = ""

    def is_ignored(self):
        '''Ignore insertion for unwanted sections. By convention, the name shall explicitly end with "+".'''
        return not self.name.endswith('+')

    def get_length(self):
        return self.end_pos - self.start_pos

    def get_sound_file_length(self):
        mp3 = MP3(os.path.abspath(self.source_filename))
        return mp3.info.length
    
    def get_timestamp_str(self, timestamp):
        minutes = int(timestamp / 60)
        seconds = timestamp - int(minutes * 60)
        return "%.2d:%.2d" % (minutes, seconds)
        
    def get_start_pos_str(self):
        return self.get_timestamp_str(self.start_pos)

    def get_end_pos_str(self):
        ceil = math.ceil(self.end_pos)
        file_length = self.get_sound_file_length()
        if ceil > file_length:
            ceil = file_length
        return self.get_timestamp_str(ceil)

    def __str__(self):
        return "Section('%s', %.2f, %.2f)" % (self.name, self.start_pos, self.end_pos)


class XSCReader(object):
    """Read XSC files from Transcribe"""

    def __init__(self, filename):
        self.markers = []
        self.filename = os.path.expanduser(filename)

        if not os.path.exists(self.filename):
            raise RuntimeError('Could not find file: %s' % self.filename)

        with open(self.filename, 'r') as inp:
            self.string = inp.read()
        self.read_section_markers()

    def get_sound_filename(self):
        for line in self.string.splitlines():
            if line.startswith('SoundFileName,'):
                filename = line.split(',')[3]
                return filename
        return None

    def get_fx_speed(self):
        for line in self.string.splitlines():
            if line.startswith('FX_Speed,'):
                speed = line.split(',')[3]
                return int(speed) / 1000
        return None
        
    def convert_timestamp_to_seconds(self, timestamp):
        hours, minutes, seconds = timestamp.split(':')
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    def get_sound_file_length(self):
        filename = self.get_sound_filename()
        mp3 = MP3(os.path.abspath(filename))
        return mp3.info.length

    def read_section_markers(self):
        section_part_open = False
        for line in self.string.splitlines():
            if line.startswith('SectionStart'):
                section_part_open = True
            elif line.startswith('SectionEnd'):
                section_part_open = False

            if not section_part_open:
                continue
            if not line.startswith('S,'):
                continue
            _, _, _, name, _, pos = line.split(",")
            marker = SectionMarker()
            marker.name = name
            marker.pos = self.convert_timestamp_to_seconds(pos)
            self.markers.append(marker)
        return True
    
    def get_marker_by_name(self, name):
        for marker in self.markers:
            if marker.name == name:
                return marker
        return None
        
    def get_sections(self):
        sections = []
        for marker in self.markers:
            if marker.name.endswith('*'):  # '*' means end section marker
                continue

            section = None
            if marker.name:
                end_marker_name = marker.name[:-1] + '*'
                end_marker = self.get_marker_by_name(end_marker_name)
                section = Section()
                section.start_pos = marker.pos
                section.name = marker.name
                section.source_filename = self.get_sound_filename()

                if end_marker is not None:
                    section.end_pos = end_marker.pos
                else:
                    marker_index = self.markers.index(marker)
                    if marker_index >= len(self.markers):
                        section.end_pos = self.get_sound_file_length()
                    else:
                        section.end_pos = self.markers[marker_index + 1].pos

            if section is not None:
                sections.append(section)
        return sections

