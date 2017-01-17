import subprocess
import glob
import sys
import os
import time

def run_hooks(hook_dir, context=None):
    if context:
        for key, value in context.iteritems():
            os.environ[key] = str(value)
            
    pre_hook_files = glob.glob('%s/*.py' % hook_dir)
    pre_hook_files.sort()
    hooks = []
    for hook_file in pre_hook_files:
        print "Starting hook", hook_file
        hook = Hook(hook_file)
        hooks.append(hook)
        result = hook.start()
        if not result:
            sys.stderr.write("Error occured while running hook: %s" % hook_file)
    return hooks

def wait_hooks(hook_list):
    for hook in hook_list:
        hook.popen.communicate()

class Hook(object):
    
    def __init__(self, cmd):
        self.cmd = cmd
        self.popen = None
        
    def start(self):
        self.popen = subprocess.Popen(self.cmd, shell=True)
        self.started = time.time()
        #stdout, stderr = popen.communicate()
        return self.popen.pid
