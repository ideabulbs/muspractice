#!/usr/bin/env python
import subprocess
import os
import sys
import signal
import time


class RemoteMachine(object):

    def __init__(self, user, ip_addr):
        self.user = user
        self.ip_addr = ip_addr
    
    def is_online(self):
        popen = subprocess.Popen(['ping', '-c', '1', self.ip_addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        popen.communicate()
        return popen.returncode == 0

    def get_output(self, cmd):
        popen = subprocess.Popen(['ssh', '%s@%s' % (self.user, self.ip_addr), cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if popen.returncode != 0:
            print stdout
            print stderr
            raise RuntimeError("Could not get output from the host")
        return stdout, stderr, popen.returncode


class RemoteMachineJack(object):

    def get_remote_jack_ports(self):
        stdout, stderr, _ = self.get_output('jack_lsp')
        ports = []
        for line in stdout.splitlines():
            ports.append(line.strip())
        return ports

    def capture(self, port_list):
        if not port_list:
            raise RuntimeError('Provide a list of JACK ports to capture output from')
        cmd = 'jack_capture -dc -f ogg '
        for port in port_list:
            cmd += ' -p ' + port
        self.capture_filename = '/home/%s/tmp/out_%d.ogg' % (self.user, os.getpid())
        cmd += ' ' + self.capture_filename

        popen = subprocess.Popen(['ssh', '%s@%s' % (self.user, self.ip_addr), cmd], preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.recording_pid = popen.pid
        return popen.pid

    def remote_cleanup(self):
        if not self.capture_filename:
            return False
        if not self.capture_filename.endswith('.ogg'):
            raise RuntimeError('No remote capture filename is set')
        cmd = 'rm -rf %s' % self.capture_filename
        popen = subprocess.Popen(['ssh', '%s@%s' % (self.user, self.ip_addr), cmd])
        popen.communicate()
        return True
            
        
class RecordingPortDiscovery(object):
    
    def get_recording_ports(self):
        ports = self.get_remote_jack_ports()
        result = []

        if not 'system:capture_3' in ports:
            raise RuntimeError('Could not find system:capture_1')
        result.append('system:capture_3')
        
        if not 'system:capture_4' in ports:
            raise RuntimeError('Could not find system:capture_4')
        result.append('system:capture_4')

        piano_ports = ['Non-Mixer/PianoL:out-1', 'Non-Mixer/PianoR:out-1']
        for port in piano_ports:
            if port in ports:
                result.append(port)

        # if not 'system:capture_3' in ports:
        #     raise RuntimeError('Could not find system:capture_3')
        # result.append('system:capture_3')

        # if not 'system:capture_4' in ports:
        #     raise RuntimeError('Could not find system:capture_4')
        # result.append('system:capture_4')

                
        return result
        
class RemoteRecorder(RemoteMachine, RemoteMachineJack, RecordingPortDiscovery):
    pass


def main():
    user = os.environ['MUSPRACTICE_REMOTE_RECORDER_USER']
    ip_addr= os.environ['MUSPRACTICE_REMOTE_RECORDER_HOST']
    rr = RemoteRecorder(user, ip_addr)
    if not rr.is_online():
        print 'Recording host is not online. Recording skipped'
        sys.exit(1)

    ports = rr.get_recording_ports()
    pid = rr.capture(ports)

    with open('remote_recording.dat', 'w') as out:
        data = "%s %s@%s %s" % (pid, rr.user, rr.ip_addr, rr.capture_filename)
        out.write(data)

if __name__ == '__main__':
    main()
