from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject
from node import Node
import requests

def SSLENode(Node):
    def init(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        self.addr = addr
        self.port = port
        self.group = ECGroup(prime192v1)
        self.shared_list = []
        super(SSLENode, self).init()
    
    def election(self):
        if (self.shared_list == []):
            self.g = self.group.random(G)
            self.broadcast_g(self.g)
            self.r = self.group.random(ZR)
            self.x = self.group.random(ZR)
            self.shared_list.append([objectToBytes(g ** r), objectToBytes(g ** (x * r)])
            self.broadcast_shared_list()
    
    def broadcast_g(self, g):
        for peer in self.peer_list:
            url = "http://{host}:{port}/broadcast_g_handler".format(host = peer["addr"], port = peer["port"])
            data = json.dumps({"g" : g})
            requests.post(url, data = data)
    
    def broadcast_shared_list(self):
        for peer in self.peer_list:
            url = "http://{host}:{port}/broadcast_shared_list_handler".format(host = peer["addr"], port = peer["port"])
            data = self.shared_list
            requests.post(url, data = data)
