import os
import subprocess
import re
import sys
import random
import argparse
import tempfile
import threading 
import time

#def thread(process, **kwargs):
#    t1 = threading.Thread(target=process, args=(**kwargs))
#
#
#def helper(func):
#    def wrapper():
#        tmpOutput = tempfile.NamedTemporaryFile(delete=True)
#        callOpenvpn()
#    pass


def callOpenvpn(vpnConf):

    def launchThread(spawn):
        def createThread(*k, **kw):
            try:
                t = threading.Thread(target=spawn, args=k, kwargs=kw)
                t.start()

            except Exception as e:
                print(e)

            finally:
                return t

        return createThread

    @launchThread
    def spawnConnectionConfig(log):
    
        print(log.name)
        #Make this not while true, instead, wait until an ip has been located
        while True:
            logFile = log.tell()
            line = log.readline().decode('utf-8')
            if not line:
                time.sleep(0.1) # Sleep briefly
                continue
            else:
                ipMatch = \
                re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line)
    
                if ipMatch is not None:
                    ip = line[ipMatch.start():ipMatch.end()]
                    print(line)
                    print(ip)
            #yield line
    
    @launchThread
    def spawnConnection(vpnConf, log):
            
        print(vpnConf.read().decode('utf-8'))
    
        cmd = "openvpn " + vpnConf.name + " > " + log.name
        cmd = "openvpn " + vpnConf.name# + " > " + log.name
        #cmd = "openvpn " + '/etc/openvpn/test3-za-jnb.prod.surfshark.com_tcp.ovpn'
        # This spawns a blocking process
        #breakpoint()
        test = subprocess.Popen(cmd, shell=False)
        #subprocess.call(cmd, shell=False)
        #subprocess.call(cmd)

    try:
        tmpLog = tempfile.NamedTemporaryFile(delete=True)
        t1 = spawnConnectionConfig(tmpLog)
        t2 = spawnConnection(vpnConf, tmpLog)

    except Exception as e:
        print(e)

    #finally:
    #    breakpoint()
    #    tmpLog.close()
    #    t1.join()
    #    t2.join()


class openvpn:

    def __init__(self, vpnDirList, tcp, udp, user, passw, vpnFile=None):
        self.vpnDirList = vpnDirList
        self.tcp = tcp
        self.udp = udp
        self.user = user
        self.passw = passw
        self.vpnFile = vpnFile if vpnFile is not None else None

        self.fileList = {}

        if vpnDirList is None and vpnFile is None:
            sys.exit('Must specify either file or dir to collection of files')

        if tcp is False and udp is False and vpnFile is None:
            sys.exit('At least one protocol must be specified if no vpn conf is\
                    specified')

        self.getVpnFiles()

    def getVpnFiles(self):
        for file in os.listdir( self.vpnDirList ):
            if self.tcp:
                if file.endswith("tcp.ovpn"):
                    self.fileList[file] = file
            if self.udp:
                if file.endswith("udp.ovpn"):
                    self.fileList[file] = file

    def getRandomVpnFile(self):
        self.vpnFile = random.choice(list(self.fileList))

    def connect(self):
        if self.vpnFile is None:
            self.getRandomVpnFile()

        # Create a path to the vpn configuration
        path = os.path.join(self.vpnDirList, self.vpnFile)

        tmpVpnFile = tempfile.NamedTemporaryFile(delete=True)
        tmpVpnAuth = tempfile.NamedTemporaryFile(delete=True)

        try:

            with open(tmpVpnAuth.name, 'w') as f:
                f.write(self.user)
                f.write('\n')
                f.write(self.passw)

            authStr = 'auth-user-pass ' + tmpVpnAuth.name
            #authStr = 'auth-user-pass ' + '/etc/openvpn/openvpn_auth.auth'

            with open(path, 'r') as f:
                c = f.read()
                cNew = re.sub(r'\bauth-user-pass\b', authStr, c, flags = re.M)

                with open(tmpVpnFile.name, 'w') as v:
                    v.write(cNew)

            #callOpenvpn(tmpVpnFile.name)
            callOpenvpn(tmpVpnFile)

        except Exception as e:
            print(e)

        finally:
            tmpVpnFile.close()
            tmpVpnAuth.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get autoconnect openvpn options')

    # Argument List
    parser.add_argument('--file', '-f',  type=argparse.FileType('r'),\
            help='Specify openvpn file to use. Takes precedence over --dir')

    parser.add_argument('--dir', '-d',  type=str,\
            help='Directory containing collection of openvpn connections')

    parser.add_argument('--tcp', action='store_true',\
            help='Allow random selection of tcp connections')

    parser.add_argument('--udp', action='store_true',\
            help='Allow random selection of udp connections')
    
    parser.add_argument('--user', '-u', type=str,\
            help='Pass username for vpn authentication')
    
    parser.add_argument('--passw', '-p', type=str,\
            help='Pass username for vpn authentication')

    args = parser.parse_args()

    vpn = openvpn( args.dir, args.tcp, args.udp, args.user, args.passw, args.file  )
    vpn.connect()

