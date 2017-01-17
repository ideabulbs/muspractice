#!/usr/bin/env python
import os
import time


def main():
    log_temp_file = 'text_log.dat'
    if os.path.exists(log_temp_file):
        os.unlink(log_temp_file)

    with open(log_temp_file, 'w') as out:
        out.write('%d' % time.time())

if __name__ == '__main__':
    main()
