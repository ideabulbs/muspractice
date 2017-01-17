#!/usr/bin/env python
import os
import sys
import time
import datetime

def cleanup():
    os.unlink('text_log.dat')

def main():
    log_temp_file = 'text_log.dat'
    if not os.path.exists(log_temp_file):
        print "No text log entry from pre-hook found"
        sys.exit(1)
    data = open(log_temp_file, 'r').read()
    start_timestamp = int(data.strip())
    duration = int(time.time() - start_timestamp)
    if duration < 130:
        print "Repetition too short. Skipping text logging..."
        cleanup()
        sys.exit(1)

    start_timestamp_string = datetime.datetime.fromtimestamp(start_timestamp).strftime('%Y-%m-%dT%H:%M:%S')
    tokens = [start_timestamp_string, str(duration), os.environ['PHRASE_ID'], os.environ['PHRASE_NAME']]
    if 'PHRASE_METRONOME_SPEED' in os.environ:
        tokens.append(os.environ['PHRASE_METRONOME_SPEED'])
    else:
        tokens.append('None')
        
    if 'PHRASE_SPEED' in os.environ:
        tokens.append(os.environ['PHRASE_SPEED'])
    else:
        tokens.append('None')
        
    log_string = '\t'.join(tokens)
    print log_string

    log_output_file = os.environ['MUSPRACTICE_RECORDING_ARCHIVE'] + '/repetitions.list'
    print log_output_file
    with open(log_output_file, 'a') as out:
        out.write(log_string + os.linesep)
    cleanup()

if __name__ == '__main__':
    main()
