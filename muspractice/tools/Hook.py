import subprocess
import glob
import sys
import os

def run_hooks(hook_dir, context=None):
    if context:
        for key, value in context.iteritems():
            os.environ[key] = str(value)
            
    pre_hook_files = glob.glob('%s/*.py' % hook_dir)
    pre_hook_files.sort()
    for hook_file in pre_hook_files:
        hook = Hook(hook_file)
        result = hook.run()
        if not result:
            sys.stderr.write("Error occured while running hook: %s" % hook_file)
            return

class Hook(object):
    
    def __init__(self, cmd):
        self.cmd = cmd
        
    def run(self):
        popen = subprocess.Popen(self.cmd, shell=True)
        stdout, stderr = popen.communicate()
        return popen.returncode == 0
