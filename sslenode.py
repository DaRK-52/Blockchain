from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject
from node import Node
from strategy import SSLEStrategy
import requests
import json

def SSLENode(Node):
    # x is the secret value of our node
    def init(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        self.addr = addr
        self.port = port
        self.id_cfg_file = addr + str(port) + "identity.json"
        # I think ECGroup can construct the same object?
        self.group = ECGroup(prime192v1)
        self.g = ""
        self.x = ""
        self.leader = []
        self.shared_list = []
        self.election_strategy = SSLEStrategy(self)
        url = "http://{dns_host}:{dns_port}/register_as_validator".format(
            dns_host = const.DEFUALT_DNS_ADDR, 
            dns_port = const.DEFAULT_DNS_PORT
        )
        r = requests.get(url = url)
        if (r.text != const.ERROR):
            self.index = int(r.text)
        super(SSLENode, self).init()
        self.validator_list = self.get_validator_list()
        self.connect_to_validator()
    
    # validator need to maintain a full connection
    def connect_to_validator(self):
        for validator in validator_list:
            # neglect oneself
            if (validator["addr"] == self.addr and validator["port"] == self.port):
                continue
            url = "http://{host}:{port}/connect_validator".format(host = validator["addr"], port = validator["port"])
            requests.get(url)

    def connection_from_validator(self, validator):
        if ({"addr": validator["addr"], "port": validator["port"]} not in self.validator_list):
            validator_list.append(validator)
    
    def election(self):
        if (self.shared_list == []):
            self.election_strategy.begin_election()
        else:
            self.election_strategy.incre_election()

    def get_validator_list(self):
        url = "http://{dns_host}:{dns_port}/get_validator_list".format(dns_host = const.DEFUALT_DNS_ADDR, dns_port = const.DEFAULT_DNS_PORT)
        r = requests.get(url = url)
        if (r.text != None):
            self.peer_list = json.loads(r.text)
            return True
        return False
    
    def broadcast_shared_list(self):
        for validator in validator_list:
            # neglect oneself
            if (validator["addr"] == self.addr and validator["port"] == self.port):
                continue
            # TODO: broadcast_shared_list_handler
            url = "http://{host}:{port}/broadcast_shared_list_handler".format(host = validator["addr"], port = validator["port"])
            requests.post(url, data = json.dumps(self.shared_list))

    def broadcast_group_primitive(self):
        for validator in validator_list:
            # neglect oneself
            if (validator["addr"] == self.addr and validator["port"] == self.port):
                continue
            url = "http://{host}:{port}/broadcast_group_primitive_handler".format(host = validator["addr"], port = validator["port"])
            requests.post(url, data = json.dumps(objectToBytes(self.g).decode()))