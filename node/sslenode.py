from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject
import requests
import json
import sys

from util.requestUtil import Urlutil, Datautil

sys.path.insert(0, sys.path[0] + "/../")
import const
from node.node import Node
from strategy.strategy import SSLEStrategy


class SSLENode(Node):
    # x is the secret value of our node
    def __init__(self, addr=const.DEFAULT_ADDR, port=const.DEFAULT_PORT):
        super().__init__(addr, port)
        self.election_strategy = None

    def init(self, addr=const.DEFAULT_ADDR, port=const.DEFAULT_PORT):
        self.addr = addr
        self.port = port
        self.id_cfg_file = addr + str(port) + "identity.json"

        url = Urlutil.make_url(const.DEFUALT_DNS_ADDR, const.DEFAULT_DNS_PORT, "register_as_validator")
        r = requests.post(url=url, data=json.dumps(Datautil.make_addr_port_dict(self)))
        self.get_validator_list()
        self.connect_to_validator()
        self.election_strategy = SSLEStrategy(self)
        if r.text != const.ERROR:
            self.election_strategy.index = int(r.text)
        super(SSLENode, self).init()

    # validator need to maintain a full connection
    def connect_to_validator(self):
        for validator in self.validator_list:
            # neglect oneself
            if self.is_self(validator):
                continue
            url = Urlutil.make_url(validator["addr"], validator["port"], "connect_validator")
            requests.post(url, data=json.dumps(Datautil.make_addr_port_dict(self)))

    def connection_from_validator(self, validator):
        if {"addr": validator["addr"], "port": validator["port"]} not in self.validator_list:
            self.validator_list.append(validator)
        return const.SUCCESS

    def begin_election(self):
        self.election_strategy.begin_election()

    def check_leader(self, x=None):
        return self.election_strategy.check_leader(x)

    def get_validator_list(self):
        url = Urlutil.make_url(const.DEFUALT_DNS_ADDR, const.DEFAULT_DNS_PORT, "get_validator_list")
        r = requests.get(url=url)
        if r.text is not None:
            self.validator_list = json.loads(r.text)
            return True
        return False

    def broadcast_identity(self):
        self.election_strategy.broadcast_identity()

    def is_self(self, obj):
        return obj["addr"] == self.addr and obj["port"] == self.port
