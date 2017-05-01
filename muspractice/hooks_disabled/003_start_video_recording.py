#!/usr/bin/python
import subprocess
import os
import sys
from xml.dom import minidom

def main():
    addr = os.environ['CAM_ADDR']
    user = os.environ['CAM_USER']
    pwd = os.environ['CAM_PASS']
    cmd = 'wget -T 2 -O - http://%s:%s@%s/axis-cgi/record/record.cgi?diskid=SD_DISK' % (user, pwd, addr)
    popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    response, stderr = popen.communicate()
    if popen.returncode != 0:
        sys.stderr.write(response)
        sys.stderr.write(stderr)
        return
    
    dom = minidom.parseString(response)
    recordings = dom.getElementsByTagNameNS('*', 'record')
    if len(recordings) == 0:
        sys.stderr.write(response)
        sys.stderr.write('Could not determine recording ID!')
        sys.exit(1)
    recording_id = recordings[0].attributes['recordingid'].value
    with open('video.rec_id', 'w') as out:
        out.write(recording_id)
    print "Video recording started: %s" % recording_id

if __name__ == '__main__':
    main()
