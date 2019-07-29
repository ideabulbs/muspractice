import configparser
import os
import sys

class Config(object):

    is_new = False
    
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = self.get_config_filename()

        self.config_file = os.path.expanduser(config_file)
        self._cfp = configparser.RawConfigParser()
        if not os.path.exists(self.config_file):
            print(("Config file %s not found. Initializing new configuration..." % self.config_file))
            if not self._init_config():
                raise RuntimeError("Could not initialize config file: %s" % self.config_file)
            self.is_new = True
        else:
            self._cfp.read(self.config_file)

    def get_config_filename(self):
        '''Get the path to the configuration file .muspracticerc.

        If .muspracticerc is found in the local directory, it will be
        used. Otherwise it is looked for in $HOME.
        '''
        config_filename = ".muspracticerc"
        if os.path.exists('./%s' % config_filename):
            config_filename = "./%s" % config_filename
        else:
            config_filename = "~/%s" % config_filename
        return config_filename

    def _init_config(self):
        '''Create a new standard config file'''
        self._cfp.add_section('General')
        self._cfp.set('General', 'audiosink', 'jackaudiosink')
        self._cfp.set('General', 'music_directory', '~/Music')
        self._cfp.set('General', 'database_file', '~/muspractice/practice_data.db')
        self._cfp.set('General', 'temporary_directory', '/tmp/')
        self._cfp.set('General', 'jack_ports', 'system:playback_1,system:playback_2')
        with open(self.config_file, 'w') as out:
            self._cfp.write(out)
        return True

    @property
    def cfp(self):
        return self._cfp

    @property
    def AUDIOSINK(self):
        return self._cfp.get('General', 'audiosink')

    @property
    def MUSIC_DIRECTORY(self):
        directory = self._cfp.get('General', 'music_directory')
        if not directory.endswith(os.sep):
            directory += os.sep
        return directory

    @property
    def DATABASE_FILE(self):
        dbfile = self._cfp.get('General', 'database_file')
        return os.path.expanduser(dbfile)
        
    @property
    def TEMPORARY_DIRECTORY(self):
        directory = self._cfp.get('General', 'temporary_directory')
        if not directory.endswith(os.sep):
            directory += os.sep
        return directory

    @property
    def RUN_HOOKS(self):
        return self._cfp.get('General', 'run_hooks')

    @property
    def JACK_PORTS(self):
        try:
            ports_str = self._cfp.get('General', 'jack_ports')
        except configparser.NoOptionError:
            print("Parameter 'jack_ports' is not set in the config file!")
            sys.exit(1)
        ports = []
        for item in ports_str.split(','):
            ports.append(item.strip())
        return ports
