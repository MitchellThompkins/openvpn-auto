import os
import subprocess
import re
import sys
import random
import argparse
import tempfile
import shutil

class openVpn():

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


        try:
            tmpVpnFile = tempfile.NamedTemporaryFile(delete=True)
            tmpVpnConf = tempfile.NamedTemporaryFile(delete=True)

            with open(tmpVpnConf.name, 'w') as f:
                f.write(self.user)
                f.write('\n')
                f.write(self.passw)

            #authStr = 'auth-user-pass /etc/openvpn/openvpn_auth.auth'
            authStr = 'auth-user-pass' + tmpVpnConf.name

            with open(path, 'r') as f:
                c = f.read()
                cNew = re.sub(r'\bauth-user-pass\b', authStr, c, flags = re.M)

                with open(tmpVpnFile.name, 'w') as v:
                    v.write(cNew)

            subprocess.call(["openvpn", tmpVpnFile.name])

        except Exception as e:
            print(e)

    def createAuthFile(self):
        pass


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

    vpn = openVpn( args.dir, args.tcp, args.udp, args.user, args.passw, args.file  )
    vpn.connect()

