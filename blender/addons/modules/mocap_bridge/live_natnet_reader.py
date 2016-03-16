from terminal_colors import bcolors

try:
    import optirx as rx
except ImportError:
    print bcolors.FAIL + "Error importing library, please install optirx by running: sudo pip install optirx"+ bcolors.ENDC
from natnet_reader import NatNetReader
from event import Event
from natnet_data import *

class LiveNatNetReader(NatNetReader):
    def __init__(self, host, multicast, port):
        super(LiveNatNetReader, self).__init__()
        self.host = host
        self.multicast = multicast
        self.port = port
        self.version = (2, 7, 0, 0)
        self.connected = False
        self.dsock = None
        self.connectionLost = Event()


    def openStream(self):
        print(bcolors.OKBLUE + "Connecting to %s : %s" % (self.host, self.port) + bcolors.ENDC)
        try:
            if self.host is None:
                self.dsock = rx.mkdatasock() #Connecting to localhost
            elif self.multicast is not None and self.port is not None:
                self.dsock = rx.mkdatasock(ip_address=self.host, multicast_address=self.multicast, port=int(self.port)) #Connecting to multicast address
            else:
                self.dsock = rx.mkdatasock(ip_address=self.host, port=int(self.port)) # Connecting to IP address
            self.connected = True
        except:
            self.connected = False
            print(bcolors.FAIL +"There was an error connecting"+ bcolors.ENDC)
            self.connectionLost()

        return self.connected

    def closeStream(self):
        self.dsock = None
        self.connected = False
        self.connectionLost()

    def readDataFrame(self):
        data = self.dsock.recv(rx.MAX_PACKETSIZE)
        packet = rx.unpack(data, version=self.version)
        if type(packet) is rx.SenderData:
            setVersion(packet.natnet_version)
        self.parse(packet)

    def parse(self, packet):
        for s in packet.skeletons:
            skel = self.getOrCreateSkeleton(s.id)
            for r in s.rigid_bodies:
                rb = RigidBody(obj=r)
                skel.addOrUpdateRigidbody(rb)

        for r in packet.rigid_bodies:
            rb = RigidBody(obj=r)
            self.addOrUpdateRigidbody(rb)