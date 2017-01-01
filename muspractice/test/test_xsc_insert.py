import time
import os
from tools.xsc import XSCReader


class TestXSCReader(object):

    def test_read_sections(self):
        xr = XSCReader('test/data/segmented_audio_file.xsc')
        assert len(xr.get_sections()) == 10

        ignored_sections = 0
        for s in xr.get_sections():
            if s.is_ignored():
                ignored_sections += 1
        assert ignored_sections == 5

        first_section = xr.get_sections()[0]
        last_section = xr.get_sections()[-1]

        print first_section.start_pos
        print last_section.end_pos
        assert first_section.start_pos == 1.402
        assert last_section.end_pos == 8.0

    def test_section(object):
        xr = XSCReader('test/data/segmented_audio_file.xsc')
        sections = xr.get_sections()
        last_section = sections[-1]

        assert last_section.name == 'J'
        
        sections.reverse()
        last_processed_section = None
        for s in sections:
            if not s.is_ignored():
                last_processed_section = s
                break

        assert last_processed_section.name == 'I+'
        assert last_processed_section.get_start_pos_str() == "00:06"
        assert last_processed_section.get_end_pos_str() == "00:07"
            
        
