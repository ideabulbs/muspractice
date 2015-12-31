#!/usr/bin/python
import os
import signal
import time
import datetime
import re
import subprocess

def main():
    pid_file = 'recording.pid'
    if os.path.exists(pid_file):
        data = open(pid_file, 'r').read()
        if data:
            pid = int(data.strip())
            print "Stopping recording in process %d" % pid
            os.kill(pid, signal.SIGINT)
        os.unlink(pid_file)
    phrase_id = os.environ['PHRASE_ID']
    int_phrase_id = phrase_id
    phrase_id = int(phrase_id)
    phrase_id = "%.6d" % phrase_id
    phrase_name = os.environ['PHRASE_NAME']
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H%M%S')
    safe_phrase_name = "".join([c for c in phrase_name if re.match(r'\w', c)])
    filename = "%s__%s__%s.mp3" % (phrase_id, timestamp, safe_phrase_name)

    title = "%s %s (%s)" % (int_phrase_id, phrase_name, timestamp)
    if os.path.exists('video.rec_id'):
        with open('video.rec_id') as inp:
            video_rec_id = inp.read().strip()
            if video_rec_id:
                title += " %s" % video_rec_id
                
    cmd = 'id3v2 -t "%s" record.mp3' % title
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()

    cmd = "mv record.mp3 ~/archive_muspractice/%s" % filename
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()

        
if __name__ == "__main__":
    main()
