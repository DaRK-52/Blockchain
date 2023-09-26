import hashlib
import random
import const
from block.block import TestBlock
import json
import requests
from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject


class Strategy():
    pass


class EStrategy(Strategy):
    def begin_election(self):
        pass

    def check_leader(self):
        pass


class CStrategy(Strategy):
    def __init__(self, node=None):
        pass

    def build_block(self):
        pass

    def check_block(self, block=None):
        pass


class PoWStrategy(CStrategy):
    def __init__(self, node=None):
        self.node = node
        self.difficulty = const.DEFAULT_POW_DIFFICULTY

    def build_block(self):
        block = TestBlock()
        for i in range(len(self.node.transaction_pool)):
            block.block_body += self.node.transaction_pool[i].msg + "\n"
        if (len(self.node.chain)):
            block.previous_hash = hashlib.sha256(str(self.node.chain[-1]).encode()).hexdigest()
        else:
            block_previous_hash = "0000000"
        block.nonce = self.mining()
        return block

    def mining(self):
        while True:
            nonce = random.random()
            hash_nonce = int(hashlib.sha256(str(nonce).encode()).hexdigest(), 16)
            if (hash_nonce < ((1 << 255) >> self.difficulty)):
                return nonce

    def check_block(self, block=None):
        if (len(self.node.chain) != 0 and block.previous_hash != hashlib.sha256(node.chain[-1])):
            return False
        if (int(hashlib.sha256(str(block.nonce).encode()).hexdigest(), 16) >= ((1 << 255) >> self.difficulty)):
            return False
        return True


class SSLEStrategy(EStrategy):
    def __init__(self, node=None):
        self.group = ECGroup(prime192v1)
        self.g = ""
        self.x = ""
        self.index = -1
        self.leader_index = -1
        self.shared_list = []
        self.validator_list = node.validator_list
        self.addr = node.addr
        self.port = node.port

    # The pulic list is empty at this time
    # we need to broadcast our group parameter g
    # and the list with our own secret value
    def begin_election(self):
        if not self.shared_list:
            self.g = self.group.random(G)
            self.broadcast_group_primitive()

        if len(self.shared_list) == self.index - 1:
            self.submit_secret()

        # TODO: support optimization later
        # if len(self.shared_list) == len(self.validator_list):
        #     self.incre_election()

    # The elected leader substitute its secret
    def incre_election(self):
        if self.check_leader():
            x = self.x
            for i in range(len(self.shared_list)):
                if self.check_secret(i, x):
                    self.substitute_secret(i)
                    break
            # temp solution, because itself won't execute broadcast_shared_list_handler
            url = "http://{dns_host}:{dns_port}/get_random_number_ssle".format(dns_host=const.DEFUALT_DNS_ADDR,
                                                                               dns_port=const.DEFAULT_DNS_PORT)
            r = requests.get(url=url)
            self.leader_index = int(r.text)
            if self.check_leader():
                self.leader = {"addr": self.addr, "port": self.port}
                print(self.addr + ":" + self.port)
                print("I'm the leader2!")
            self.broadcast_identity()

    def substitute_secret(self, index):
        self.shared_list.pop(index)
        self.submit_secret()

    def submit_secret(self):
        r = self.group.random(ZR)
        self.x = self.group.random(ZR)
        self.shared_list.append([objectToBytes(self.g ** r, self.group).decode(),
                                      objectToBytes(self.g ** (self.x * r), self.group).decode()])
        self.shuffle()
        self.broadcast_shared_list()

    # Every time we start ssle, we need to blind and shuffle the list
    def shuffle(self):
        temp_list = []
        r = self.group.random(ZR)
        for item in self.shared_list:
            u = bytesToObject(item[0].encode(), self.group)
            v = bytesToObject(item[1].encode(), self.group)
            temp_list.append(
                [objectToBytes(u ** r, self.group).decode(), objectToBytes(v ** r, self.group).decode()])
        self.shared_list = temp_list
        random.shuffle(self.shared_list)

    def check_leader(self, x=None):
        if not x:
            x = self.x
        return self.check_secret(self.leader_index, x)

    # check whether shared_list[index] belongs to oneself
    def check_secret(self, index, x):
        u = bytesToObject(self.shared_list[index][0].encode(), self.group)
        v = bytesToObject(self.shared_list[index][1].encode(), self.group)
        if (u ** x == v):
            return True
        return False

    def broadcast_shared_list(self):
        shared_list = self.shared_list
        for validator in self.validator_list:
            if self.is_self(validator):
                continue
            print(validator["addr"] + ":" + validator["port"])
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
