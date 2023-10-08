import hashlib
import random
import const
from block.block import TestBlock
import json
import requests
from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject

from util.requestUtil import Urlutil


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
        self.leader = {}
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

        # in round 1, request from /begin_election and
        # /broadcast_shared_list_handler will trigger
        # begin_election twice, need to avoid it
        if len(self.shared_list) == self.index - 1 and not self.leader:
            self.submit_secret()
            if self.index == 1:
                return

        # no need to check if validator list if full because
        # after round 1, validator is always full
        if self.leader and self.check_leader():
            self.substitute_secret()

        # leave check_leader false alone
        if len(self.shared_list) == len(self.validator_list):
            self.request_election_result_and_broadcast_if_leader()

    def submit_secret(self):
        r = self.group.random(ZR)
        self.x = self.group.random(ZR)
        self.shared_list.append([objectToBytes(self.g ** r, self.group).decode(),
                                 objectToBytes(self.g ** (self.x * r), self.group).decode()])
        self.shuffle()
        self.broadcast_shared_list()

    def substitute_secret(self):
        for i in range(len(self.shared_list)):
            if self.check_secret(i, self.x):
                self.shared_list.pop(i)
                self.submit_secret()
                break

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

    def request_election_result_and_broadcast_if_leader(self):
        url = Urlutil.make_url(const.DEFUALT_DNS_ADDR, const.DEFAULT_DNS_PORT, "get_random_number_ssle")
        r = requests.get(url=url)
        self.leader_index = int(r.text)
        if self.check_leader():
            print("I'm leader")
            self.leader = {"addr": self.addr, "port": self.port}
            self.broadcast_identity()

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
            url = Urlutil.make_url(validator["addr"], validator["port"], "broadcast_shared_list_handler")
            requests.post(url, data=json.dumps(shared_list))

    def broadcast_group_primitive(self):
        for validator in self.validator_list:
            if self.is_self(validator):
                continue
            url = Urlutil.make_url(validator["addr"], validator["port"], "broadcast_group_primitive_handler")
            requests.post(url, data=json.dumps(objectToBytes(self.g, self.group).decode()))

    def broadcast_identity(self):
        for validator in self.validator_list:
            if self.is_self(validator):
                continue
            url = Urlutil.make_url(validator["addr"], validator["port"], "broadcast_identity_handler")
            requests.post(url, data=json.dumps({
                "addr": self.addr,
                "port": self.port,
                "x": objectToBytes(self.x, self.group).decode()
            }))

    def is_self(self, obj):
        return obj["addr"] == self.addr and obj["port"] == self.port
