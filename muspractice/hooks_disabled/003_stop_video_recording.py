#!/usr/bin/python
import subprocess
import os
import sys


def main():
    addr = os.environ['CAM_ADDR']
    user = os.environ['CAM_USER']
    pwd = os.environ['CAM_PASS']
    rec_id_file = 'video.rec_id'
    if not os.path.exists(rec_id_file):
        return
    with  open(rec_id_file, 'r') as inp:
        recording_id = inp.read().strip()
        
    cmd = 'wget -T 2 -O - http://%s:%s@%s/axis-cgi/record/stop.cgi?recordingid=%s' % (user, pwd, addr, recording_id)
    popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = popen.communicate()
    if popen.returncode != 0:
        sys.stderr.write(stderr)
        sys.stderr.write('Could not stop recording %s' % recording_id)
        sys.exit(1)
    os.unlink(rec_id_file)

if __name__ == '__main__':
    main()
