#!/usr/bin/env python
import os
import sys
import time
import subprocess

def cleanup():
    os.unlink('reaper.lock')

def main():
    if not os.path.exists('reaper.lock'):
        sys.exit(0)

    ip_addr = '10.0.2.2'
    popen = subprocess.Popen('wget -O - http://%s:5000/stop' % ip_addr, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate()
    if 'ok' not in stdout:
        print "Could not close Reaper! Already closed?"
        sys.exit(1)
    cleanup()

if __name__ == '__main__':
    main()
