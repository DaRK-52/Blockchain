from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject
from node import Node
from strategy import SSLEStrategy
import requests

def SSLENode(Node):
    def init(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        self.addr = addr
        self.port = port
        self.id_cfg_file = addr + str(port) + "identity.json"
        self.group = ECGroup(prime192v1)
        self.shared_list = []
        self.leader = []
        self.election_strategy = SSLEStrategy(self)
        url = "http://{dns_host}:{dns_port}/register_as_validator".format(
            dns_host = const.DEFUALT_DNS_ADDR, 
            dns_port = const.DEFAULT_DNS_PORT
        )
        r = requests.get(url = url)
        super(SSLENode, self).init()
    
    def election(self):
        if (self.shared_list == []):
            self.election_strategy.begin_election()
        else:
            self.election_strategy.incre_election()
        if (self.shared_list == []):
            self.g = self.group.random(G)
            self.broadcast_g(self.g)
            self.r = self.group.random(ZR)
            self.x = self.group.random(ZR)
            self.shared_list.append([objectToBytes(g ** r), objectToBytes(g ** (x * r))])
            self.broadcast_shared_list()
