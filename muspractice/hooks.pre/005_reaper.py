#!/usr/bin/env python
import subprocess
import os
import sys
import signal
import time
import shutil
import requests


class RemoteMachine(object):

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
        self.server_url = "http://%s:5000" % ip_addr
        self.timeout = 5
    
    def is_online(self):
        popen = subprocess.Popen(['ping', '-c', '1', self.ip_addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        popen.communicate()
        return popen.returncode == 0

    def is_reaper_service_running(self):
        if not self.is_online():
            return False
        response = requests.get(self.server_url + "/test", timeout=self.timeout)
        if response.status_code != 200:
            print response.text
            raise RuntimeError('Reaper service running on %s, but the server returned an invalid response: %s' % (self.server_url,
                                                                                                                  response.status_code))
        return response.text == 'test ok'

    def project_exists(self, project_id):
        url = self.server_url + "/project_exists?project_id=%s" % project_id
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != 200:
            print response.text
            raise RuntimeError('Incorrect response received from %s: %s' % (url, response.status_code))
        return response.text == 'true'

    def create_project(self, project_id):
        url = self.server_url + "/create_project?project_id=%s" % project_id
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != 200:
            print response.text
            raise RuntimeError('Incorrect response received from %s: %s' % (url, response.status_code))
        return response.text == 'ok'

    def start_project(self, project_id):
        url = self.server_url + "/start?project_id=%s" % project_id
        response = requests.get(url, timeout=self.timeout)
        if response.status_code != 200:
            print response.text
            raise RuntimeError('Incorrect response received from %s: %s' % (url, response.status_code))
        return response.text == 'ok'
            
    
class ReaperProject(object):

    def __init__(self, phrase_id):
        self.phrase_id = phrase_id

    def get_project_id(self):
        return "%.6d" % int(self.phrase_id)

            
def main():
    if os.environ.get('MUSPRACTICE_REAPER_HOST') is None:
        print 'Reaper host is not set (MUSPRACTICE_REAPER_HOST)'
        return

    ip_addr = os.environ['MUSPRACTICE_REAPER_HOST']
    rr = RemoteMachine(ip_addr)

    if not rr.is_reaper_service_running():
        print "Reaper host is not online. Skipped"
        sys.exit(1)

    rp = ReaperProject(os.environ.get('PHRASE_ID'))
    project_id = rp.get_project_id()
    if not rr.project_exists(project_id):
        print "Project not found. Creating"
        if not rr.create_project(project_id):
            print "Could not create Reaper project from template!"
            sys.exit(1)

    if not rr.start_project(project_id):
        print "Could not start Reaper!"
        sys.exit(1)

    with open('reaper.lock', 'w') as out:
        data = "%s" % (rr.ip_addr)
        out.write(data)

if __name__ == '__main__':
    main()
