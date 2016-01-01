import ConfigParser
import os


class Config(object):

    is_new = False
    
    def __init__(self, config_file):
        self.config_file = os.path.expanduser(config_file)
        self._cfp = ConfigParser.RawConfigParser()
        if not os.path.exists(self.config_file):
            print "Config file %s not found. Initializing new configuration..." % self.config_file
            if not self._init_config():
                raise RuntimeError("Could not initialize config file: %s" % self.config_file)
            self.is_new = True
        else:
            self._cfp.read(self.config_file)
            
    def _init_config(self):
        self._cfp.add_section('General')
        self._cfp.set('General', 'audiosink', 'jackaudiosink')
        self._cfp.set('General', 'music_directory', '~/Music')
        self._cfp.set('General', 'database_file', '~/muspractice/practice_data.db')
        self._cfp.set('General', 'temporary_directory', '/tmp/')
        self._cfp.set('General', 'run_hooks', 'n')
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
    def RUN_HOOKS(self):
        return self._cfp.get('General', 'run_hooks')

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
