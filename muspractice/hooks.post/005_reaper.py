#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import requests


class RemoteMachine(object):

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        self.server_url = "http://%s:5000" % ip_addr
        self.timeout = 5

    def stop_reaper(self):
        url = self.server_url + "/stop"
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != 200:
            print((response.text))
            raise RuntimeError('Incorrect response received from %s: %s' % (url, response.status_code))
        return response.text == 'ok'

def cleanup():
    os.unlink('reaper.lock')

def main():
    if not os.path.exists('reaper.lock'):
        sys.exit(0)
    ip_addr = os.environ['MUSPRACTICE_REAPER_HOST']
    rr = RemoteMachine(ip_addr)
    if not rr.stop_reaper():
        print("Could not close Reaper! Already closed?")
        sys.exit(1)
    cleanup()

if __name__ == '__main__':
    main()
