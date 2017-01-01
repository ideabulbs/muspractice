'''
Copyright (c) 2011 Joar Wandborg <http://wandborg.se>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

- A response to http://stackoverflow.com/questions/8187257/play-audio-and-video-with-a-pipeline-in-gstreamer-python/8197837
- Like it? Buy me a beer! https://flattr.com/thing/422997/Joar-Wandborg
'''
import gst
import gobject
gobject.threads_init()
import logging


logging.basicConfig()

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


class VideoPlayer(object):
    '''
    Simple video player
    '''

    source_file = None

    def __init__(self, **kwargs):
        self.loop = gobject.MainLoop()

        if kwargs.get('src'):
            self.source_file = kwargs.get('src')

        self.__setup()

    def run(self):
        self.loop.run()

    def stop(self):
        self.loop.quit()

    def __setup(self):
        _log.info('Setting up VideoPlayer...')
        self.__setup_pipeline()
        _log.info('Set up')

    def __setup_pipeline(self):
        self.pipeline = gst.Pipeline('video-player-pipeline')

        # Source element
        self.filesrc = gst.element_factory_make('filesrc')
        self.filesrc.set_property('location', self.source_file)
        self.pipeline.add(self.filesrc)

        # Demuxer
        self.decoder = gst.element_factory_make('decodebin2')
        self.decoder.connect('pad-added', self.__on_decoded_pad)
        self.pipeline.add(self.decoder)

        # Video elements
        self.videoqueue = gst.element_factory_make('queue', 'videoqueue')
        self.pipeline.add(self.videoqueue)

        self.autovideoconvert = gst.element_factory_make('autovideoconvert')
        self.pipeline.add(self.autovideoconvert)

        self.autovideosink = gst.element_factory_make('autovideosink')
        self.pipeline.add(self.autovideosink)

        # Audio elements
        #self.audioqueue = gst.element_factory_make('queue', 'audioqueue')
        #self.pipeline.add(self.audioqueue)

        #self.audioconvert = gst.element_factory_make('audioconvert')
        #self.pipeline.add(self.audioconvert)

        #self.autoaudiosink = gst.element_factory_make('autoaudiosink')
        #self.pipeline.add(self.autoaudiosink)

        self.progressreport = gst.element_factory_make('progressreport')
        self.progressreport.set_property('update-freq', 1)
        self.pipeline.add(self.progressreport)

        # Link source and demuxer
        linkres = gst.element_link_many(
            self.filesrc,
            self.decoder)

        if not linkres:
            _log.error('Could not link source & demuxer elements!\n{0}'.format(
                    linkres))

        linkres = gst.element_link_many(
            self.audioqueue,
            self.audioconvert,
            self.autoaudiosink)

        if not linkres:
            _log.error('Could not link audio elements!\n{0}'.format(
                    linkres))

        linkres = gst.element_link_many(
            self.videoqueue,
            self.progressreport,
            self.autovideoconvert,
            self.autovideosink)

        if not linkres:
            _log.error('Could not link video elements!\n{0}'.format(
                    linkres))

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.__on_message)

        self.pipeline.set_state(gst.STATE_PLAYING)

    def __on_decoded_pad(self, pad, data):
        _log.debug('on_decoded_pad: {0}'.format(pad))

        if pad.get_caps()[0].to_string().startswith('audio'):
            pad.link(self.audioqueue.get_pad('sink'))
        else:
            pad.link(self.videoqueue.get_pad('sink'))

    def __on_message(self, bus, message):
        _log.debug(' - MESSAGE: {0}'.format(message))
        

if __name__ == '__main__':
    player = VideoPlayer(
        src='intro.mp4')

    player.run()
