from django.core import serializers
from models import Phrase, MetronomeSetup
import json

class Wrapper(object):
    phrase = None
    metronome_setup = None
    # def __init__(self, phrase, metronome_setup):
    #     self.phrase = phrase
    #     self.metronome_setup = metronome_setup
        
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)    

def as_wrapper(dct):
    print "arg:", dct
    w = Wrapper()
    w.phrase = dct['phrase']
    w.metronome_setup = dct['metronome_setup']
    return w
    
class JSONSerializator(object):
    def __init__(self, filename, phrase=None, metronome_setup=None):
        self._filename = filename
        self._phrase = phrase
        self._metronome_setup = metronome_setup

    def write(self):
        
        return True
        
    # def write(self):
    #     wrapper = Wrapper()
    #     wrapper.phrase = self._phrase
    #     wrapper.metronome_setup = self._metronome_setup
    #     pretty_out = wrapper.to_json()
    #     with open(self._filename, "w") as out:
    #         out.write(pretty_out)
    #     return True
    
    def read(self):
        with open(self._filename, "r") as inp:
            data = inp.read()
        print "Data", data
        wrapper = json.loads(data, object_hook=as_wrapper)
        result = {}
        result['Phrase'] = wrapper.phrase
        result['MetronomeSetup'] = wrapper.metronome_setup
        return result
