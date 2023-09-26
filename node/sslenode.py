from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject
import requests
import json
import sys

sys.path.insert(0, sys.path[0] + "/../")
import const
from node.node import Node
from strategy.strategy import SSLEStrategy


class SSLENode(Node):
    # x is the secret value of our node
    def init(self, addr=const.DEFAULT_ADDR, port=const.DEFAULT_PORT):
        self.addr = addr
        self.port = port
        self.id_cfg_file = addr + str(port) + "identity.json"
        # I think ECGroup can construct the same object?
        self.group = ECGroup(prime192v1)
        self.g = ""
        self.x = ""
        self.leader = []
        self.leader_index = -1
        self.shared_list = []
        self.election_strategy = SSLEStrategy(self)
        self.has_leader = False # TODO: only for temporary use
        url = "http://{dns_host}:{dns_port}/register_as_validator".format(
            dns_host=const.DEFUALT_DNS_ADDR,
            dns_port=const.DEFAULT_DNS_PORT
        )
        r = requests.post(url=url, data=json.dumps({
            "addr": self.addr,
            "port": self.port
        }))
        if (r.text != const.ERROR):
            self.index = int(r.text)
        super(SSLENode, self).init()
        self.get_validator_list()
        self.connect_to_validator()

    # validator need to maintain a full connection
    def connect_to_validator(self):
        for validator in self.validator_list:
            # neglect oneself
            if self.is_self(validator):
                continue
            url = "http://{host}:{port}/connect_validator".format(host=validator["addr"], port=validator["port"])
            requests.post(url, data=json.dumps({
                "addr": self.addr,
                "port": self.port
            }))

    def connection_from_validator(self, validator):
        if ({"addr": validator["addr"], "port": validator["port"]} not in self.validator_list):
            self.validator_list.append(validator)
        return const.SUCCESS

    def begin_election(self):
        self.election_strategy.begin_election()

    def check_leader(self, x=None):
        return self.election_strategy.check_leader(x)

    def get_validator_list(self):
        url = "http://{dns_host}:{dns_port}/get_validator_list".format(dns_host=const.DEFUALT_DNS_ADDR,
                                                                       dns_port=const.DEFAULT_DNS_PORT)
        r = requests.get(url=url)
        if r.text is not None:
            self.validator_list = json.loads(r.text)
            return True
        return False

    def broadcast_shared_list(self):
        shared_list = self.shared_list
        for validator in self.validator_list:
            if self.is_self(validator):
                continue
            print(validator["addr"] + ":"  + validator["port"])
            url = "http://{host}:{port}/broadcast_shared_list_handler".format(host=validator["addr"],
                                                                              port=validator["port"])
            requests.post(url, data=json.dumps(shared_list))

    def broadcast_group_primitive(self):
        for validator in self.validator_list:
            if self.is_self(validator):
                continue
            url = "http://{host}:{port}/broadcast_group_primitive_handler".format(host=validator["addr"],
                                                                                  port=validator["port"])
            requests.post(url, data=json.dumps(objectToBytes(self.g, self.group).decode()))

    def broadcast_identity(self):
        for validator in self.validator_list:
            if self.is_self(validator):
                continue
            url = "http://{host}:{port}/broadcast_identity_handler".format(host=validator["addr"],
                                                                           port=validator["port"])
            requests.post(url, data=json.dumps({
                "addr": self.addr,
                "port": self.port,
                "x": objectToBytes(self.x, self.group).decode()
            }))

    def is_self(self, obj):
        return obj["addr"] == self.addr and obj["port"] == self.port
