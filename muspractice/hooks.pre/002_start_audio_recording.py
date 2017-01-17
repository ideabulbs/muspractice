#!/usr/bin/python
import subprocess
import os

def main():
    cmd = 'jack_capture -p system:playback_2 -p system:capture_3 -c 2 -mp3 -mp3q 0 -mp3b 128 -fn record.mp3'
    popen = subprocess.Popen(cmd.split(), shell=False, preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print 'Recording started in process #%d' % popen.pid
    with open('recording.pid', 'w') as out:
        out.write('%d' % popen.pid)

if __name__ == '__main__':
    main()
