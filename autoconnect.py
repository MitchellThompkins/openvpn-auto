import os
import subprocess
import re
import sys
import random
import argparse
import tempfile
import shutil

class openVpn():

    def __init__(self, vpnDirList, tcp, udp, vpnFile=None):
        self.vpnDirList = vpnDirList
        self.tcp = tcp
        self.udp = udp
        self.vpnFile = vpnFile if vpnFile is not None else None
        self.fileList = {}

        if vpnDirList is None and vpnFile is None:
            sys.exit('Must specify either file or dir to collection of files')

        if tcp is False and udp is False and vpnFile is None:
            sys.exit('At least one protocol must be specified')

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

        path = os.path.join(self.vpnDirList, self.vpnFile)

        path = os.path.join("/etc/openvpn", "test-za-jnb.prod.surfshark.com_tcp.ovpn")

        #try:
        tmpPath = tempfile.NamedTemporaryFile(delete=True)

        #shutil.copy(path, tmpPath.name)

        editFile = 'auth-user-pass /etc/openvpn/openvpn_auth.auth'

        content_u = tmpPath.read().decode('utf-8')

        #print(content_u)

        #re.sub('\bauth-user-pass\b', 'test', content)

        with open (tmpPath.name, 'r') as f:
            content = f.read()
            #print(content)
            #content_new = re.sub('\bauth-user-pass\b', 'test', content, flags = re.M)
            content_new = re.sub(r'\bauth-user-pass\b', editFile, content, flags = re.M)

            print(content_new)

        print('\n------------------------\n')

        #content = tmpPath.read().decode('utf-8')
        #print(content)

        print(tmpPath.name)
        #subprocess.call(["openvpn", tmpPath.name])

            #subprocess.call(["openvpn", tmpPath.name])

        #except:
        #    print("Couldn't create temporary file")

        #subprocess.call(["openvpn", path])
        #p = subprocess.Popen(["openvpn", path])#, shell=True)#, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        #p.wait()



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get autoconnect openvpn options')

    # Argument List
    parser.add_argument('--dir', '-d',  type=str,\
            help='Directory containing collection of openvpn connections')
    parser.add_argument('--file', '-f',  type=argparse.FileType('r'),\
            help='Specify openvpn file to use. Takes precedence over --dir')
    parser.add_argument('--tcp', '-t', action='store_true',\
            help='Allow tcp connections')
    parser.add_argument('--udp', '-u', action='store_true',\
            help='Allow udp connections')

    args = parser.parse_args()

    vpn = openVpn( args.dir, args.tcp, args.udp, args.file )
    vpn.connect()

