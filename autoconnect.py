import os
import subprocess
import re
import sys
import random
import argparse
import tempfile
import threading 
import time


def launchAutoOpenvpn(vpnConf, localExceptions):
    """launchAutoOpenvpn

    @brief

    @Pre

    @Post

    @return None """


    def controlUfw(localExceptions, vpnException):
        """launchAutoOpenvpn

        @brief

        @Pre

        @Post

        @return None """

        commandList = []
        commandList.append('sudo ufw default deny outgoing')
        commandList.append('sudo ufw default deny incoming')

        for entry in localExceptions:
            commandList.append( 'sudo ufw allow in to ' + str(entry))
            commandList.append( 'sudo ufw allow out to ' + str(entry))

        commandList.append('sudo ufw allow out to ' + vpnException +\
                ' port 1443 proto tcp')
        commandList.append('sudo ufw allow out on tun0 from any to any')
        commandList.append('ufw enable')

        for entry in commandList:
            subprocess.call(entry, shell=True)


    def monitorStatus(log, localExceptions):
        """monitorStatus

        @brief monitors a log file which has been passed for ip's and vpn
        connectivity

        @Pre A file from which can content can be read

        @Post
    
        @return None """

        #Make this not while true, instead, wait until an ip has been located
        ipDetected = False
        while not ipDetected:
            logFile = log.tell()
            line = log.readline().decode('utf-8')

            if not line:
                time.sleep(0.1)
                continue
            else:
                # Regex for an ip address
                ipMatch = \
                re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line)
    
                if ipMatch is not None:
                    ip = line[ipMatch.start():ipMatch.end()]
                    controlUfw(localExceptions, ip)
                    ipDetected = True
                    print(line)
                    #print(ip)
            #yield line
    
    def startConnection(vpnConf, log):
        """startConnection
    
        @brief This spins up a blocking task which directs output to the
        specified provided file
    
        @Pre A vpn configuration file vpnConf has been passed which is correctly
        formatted
    
        @Pre A file to be used as a log to which content can be written
    
        @Post
    
        @return None
        """
        cmd = "openvpn " + vpnConf.name + " > " + log.name
        subprocess.call(cmd, shell=True)

    try:
        tmpLog = tempfile.NamedTemporaryFile(delete=True)

        t1 = threading.Thread(target=startConnection,\
                args=(vpnConf, tmpLog))
        t2 = threading.Thread(target=monitorStatus,\
                args=(tmpLog, localExceptions))

        t1.start()
        t2.start()

    except Exception as e:
        print(e)

    finally:
        t1.join()
        t2.join()
        tmpLog.close()


class autoOpenvpnConf:

    def __init__(self, vpnDirList, tcp, udp, user, passw,\
            networkAllowList, vpnFile=None):

        self.vpnDirList = vpnDirList
        self.tcp = tcp
        self.udp = udp
        self.user = user
        self.passw = passw
        self.networkAllowList = networkAllowList
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

    def start(self):
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

            with open(path, 'r') as f:
                c = f.read()
                cNew = re.sub(r'\bauth-user-pass\b', authStr, c, flags = re.M)

                with open(tmpVpnFile.name, 'w') as v:
                    v.write(cNew)

            launchAutoOpenvpn(tmpVpnFile, self.networkAllowList)

        except Exception as e:
            print(e)

        finally:
            tmpVpnFile.close()
            tmpVpnAuth.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=\
            'Get autoconnect openvpn options')

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

    parser.add_argument('--local', '-l', action='store_true',\
            help='Configure ufw to allow access on typical local nets\
            192.168.0.X and 192.168.1.X on lan and wlan')

    parser.add_argument('--specify_net', '-s', type=str, nargs='+',\
            help='Configure ufw to allow access on provided specifc nets')

    args = parser.parse_args()


    networkList = []
    if(args.local):
        networkList.append('192.168.0.0/24')
        networkList.append('192.168.1.0/24')
    else:
        networkList = args.specify_net

    vpn = autoOpenvpnConf\
            ( args.dir, args.tcp, args.udp, args.user, args.passw,\
            networkList, args.file )

    vpn.start()

