#!/usr/bin/env python
import subprocess
import os
import sys
import signal
import time
import shutil

class RemoteMachine(object):

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr
    
    def is_online(self):
        popen = subprocess.Popen(['ping', '-c', '1', self.ip_addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        popen.communicate()
        return popen.returncode == 0

class ReaperProject(object):

    def __init__(self, phrase_id):
        self.phrase_id = phrase_id
        self.projects_subdir = os.path.expanduser('~/repmusic/reaper/')

    def get_project_name(self):
        return "%.6d" % int(self.phrase_id)
    
    def get_full_file_path(self):
        return "%s/%s/%s.RPP" % (self.projects_subdir, self.get_project_name(), self.get_project_name())
    
    def get_full_dir_path(self):
        return "%s/%s.RPP" % (self.projects_subdir, self.get_project_name())

    def is_created(self):
        if os.path.exists(self.get_full_file_path()):
            return True
        return False

    def create(self):
        if os.path.exists(self.get_full_file_path()):
            return False
        src_dir = '%stemplate' % self.projects_subdir
        dst_dir = '%s%s' % (self.projects_subdir, self.get_project_name())
        shutil.copytree(src_dir, dst_dir)
        shutil.move('%s/template.RPP' % (dst_dir), '%s/%s.RPP' % (dst_dir, self.get_project_name()))
        return True
        
def main():
    ip_addr = '10.0.2.2'
    rr = RemoteMachine(ip_addr)
    if not rr.is_online():
        print 'Reaper host is not online. Recording skipped'
        sys.exit(1)

    popen = subprocess.Popen('wget -O - http://%s:5000/test' % ip_addr, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate()
    if 'test ok' not in stdout:
        print "Reaper host is not online. Skipped"
        sys.exit(1)

    rp = ReaperProject(os.environ.get('PHRASE_ID'))
    if not rp.is_created():
        print "Project not found. Creating"
        if not rp.create():
            print "Could not create Reaper project from template!"
            sys.exit(1)

    popen = subprocess.Popen('wget -O - http://%s:5000/start?project_id=%s' % (ip_addr, rp.get_project_name()), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate()
    if 'ok' not in stdout:
        print "Could not start Reaper!"
        sys.exit(1)

    with open('reaper.lock', 'w') as out:
        data = "%s" % (rr.ip_addr)
        out.write(data)

if __name__ == '__main__':
    main()
    # rp = ReaperProject(1869)
    # print rp.is_created()
    # print rp.create()
