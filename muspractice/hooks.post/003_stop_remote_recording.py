#!/usr/bin/env python
import os
import signal
import subprocess
import sys
import time
import datetime
import re


def get_file():
    data_file = 'remote_recording.dat'
    if not os.path.exists(data_file):
        print "No data file found from remote recording pre-hook"
        sys.exit(1)
        
    pid, remote_machine, filename = open(data_file, 'r').read().split()
    print "Stopping remote recording in process %s" % pid
    try:
        os.kill(int(pid), signal.SIGINT)
    except OSError:
        print "Process %s already finished?" % pid

    local_filename = 'recording.ogg'
    popen = subprocess.Popen(['scp', remote_machine + ':' +filename, local_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen.communicate()
    if popen.returncode != 0:
        raise RuntimeError('Could not transfer file %s from remote recorder %s' % (filename, remote_machine))

    if not filename:
        raise RuntimeError('Invalid remote capture filename: %s' % filename)
    if not filename.endswith('.ogg'):
        raise RuntimeError('Invalid remote capture filename "%s"' % filename)

    cmd = 'rm -rf %s' % filename
    popen = subprocess.Popen(['ssh', remote_machine, cmd])
    popen.communicate()
    if popen.returncode != 0:
        raise RuntimeError('Could not perform cleanup on remote recorder: %s:%s' % (remote_machine, filename))
    os.unlink(data_file)
    return local_filename

def get_duration(filename):
    popen = subprocess.Popen(['ogginfo', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate()
    if popen.returncode != 0:
        print stdout
        print stderr
        raise RuntimeError('Could not get ogg file data with ogginfo: ogginfo %s' % filename)
    length_line = ""
    for line in stdout.splitlines():
        if 'Playback length:' in line:
            length_line = line.strip()
            break
    else:
        print stdout
        print stderr
        raise RuntimeError('Could not read file metadata with ogginfo: ogginfo %s' % filename)
    tokens = length_line.split('length: ')
    duration = tokens[1]
    tokens = duration.split(':')
    minutes = int(tokens[0][:-1])
    seconds = float(tokens[1][:-1])
    return minutes * 60 + seconds
    
def set_metadata(filename):
    phrase_id = os.environ['PHRASE_ID']
    int_phrase_id = phrase_id
    phrase_id = int(phrase_id)
    phrase_id = "%.6d" % phrase_id
    phrase_name = os.environ['PHRASE_NAME']
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H%M%S')
    safe_phrase_name = "".join([c for c in phrase_name if re.match(r'\w', c)])
    new_filename = "%s__%s__%s.ogg" % (phrase_id, timestamp, safe_phrase_name)

    title = "%s %s (%s)" % (int_phrase_id, phrase_name, timestamp)
    if 'PHRASE_METRONOME_SPEED' in os.environ:
        title += " (%s BPM)" % os.environ['PHRASE_METRONOME_SPEED']
    elif 'PHRASE_SPEED' in os.environ:
        title += " (%s%% speed)" % os.environ['PHRASE_SPEED']
                
    cmd = 'id3v2 -t "%s" %s' % (title, filename)
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()
    if popen.returncode != 0:
        raise RuntimeError('Could not set metadata on local file: %s' % filename)

    cmd = 'mv %s %s/%s' % (filename, os.environ['MUSPRACTICE_RECORDING_ARCHIVE'], new_filename)
    popen = subprocess.Popen(cmd, shell=True)
    popen.communicate()
    if popen.returncode != 0:
        raise RuntimeError('Could not rename: %s %s' % (filename, new_filename))
    return new_filename

def main():
    filename = get_file()
    duration = get_duration(filename)
    if duration < 130:
        print "Remote recording too short (%.2f seconds). Removing..." % duration
        os.unlink(filename)
    else:
        set_metadata(filename)
    
if __name__ == '__main__':
    main()
