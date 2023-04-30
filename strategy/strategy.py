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
    def __init__(self, node = None):
        self.node = node
    
    def build_block(self):
        pass
    
    def check_block(self):
        pass

class PoWStrategy(CStrategy):
    def __init__(self, node = None):
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
            if(hash_nonce < ((1 << 255) >> self.difficulty)):
                return nonce

    def check_block(self, block = None):
        if(len(self.node.chain) != 0 and block.previous_hash != hashlib.sha256(node.chain[-1])):
            return False
        if(int(hashlib.sha256(str(block.nonce).encode()).hexdigest(), 16) >= ((1 << 255) >> self.difficulty)):
            return False
        return True

class SSLEStrategy(EStrategy):
    def __init__(self, node = None):
        self.node = node
    
    # The pulic list is empty at this time
    # we need to broadcast our group parameter g
    # and the list with our own secret value
    def begin_election(self):
        if (self.node.shared_list == []):
            self.node.g = self.node.group.random(G)
            self.node.broadcast_group_primitive()

        r = self.node.group.random(ZR)
        self.node.x = self.node.group.random(ZR)
        self.node.shared_list.append([objectToBytes(self.node.g ** r, self.node.group).decode(), objectToBytes(self.node.g ** (self.node.x * r), self.node.group).decode()])
        self.shuffle()
        self.node.broadcast_shared_list()
    
    # The elected leader substitute its secret
    def incre_election(self):
        if (self.check_leader()):
            x = self.node.x
            for i in range(len(self.node.shared_list)):
                if (self.check_secret(i, x)):
                    self.substitute_secret(i)
                    self.shuffle()
                    self.node.broadcast_shared_list()
                    break
            url = "http://{dns_host}:{dns_port}/get_random_number_ssle".format(dns_host = const.DEFUALT_DNS_ADDR, dns_port = const.DEFAULT_DNS_PORT)
            r = requests.get(url = url)
            self.node.leader_index = int(r.text)
            print(self.node.check_leader())
            if (self.node.check_leader()):
                self.node.leader = {"addr": self.node.addr, "port": self.node.port}
                print(self.node.addr + ":" + self.node.port)
                print("I'm the leader!")
            self.node.broadcast_identity()
    
    # Every time we start ssle, we need to blind and shuffle the list
    def shuffle(self):
        temp_list = []
        r = self.node.group.random(ZR)
        for item in self.node.shared_list:
            u = bytesToObject(item[0].encode(), self.node.group)
            v = bytesToObject(item[1].encode(), self.node.group)
            temp_list.append([objectToBytes(u ** r, self.node.group).decode(), objectToBytes(v ** r, self.node.group).decode()])
        self.node.shared_list = temp_list
        random.shuffle(self.node.shared_list)
    
    def check_leader(self, x = None):
        if (not x):
            x = self.node.x
        return self.check_secret(self.node.leader_index, x)
    
    # check whether shared_list[index] belongs to oneself
    def check_secret(self, index, x):
        u = bytesToObject(self.node.shared_list[index][0].encode(), self.node.group)
        v = bytesToObject(self.node.shared_list[index][1].encode(), self.node.group)
        if (u ** x == v):
            return True
        return False
    
    def substitute_secret(self, index):
        self.node.shared_list.pop(index)
        r = self.node.group.random(ZR)
        self.node.shared_list.append([objectToBytes(self.node.g ** r, self.node.group).decode(), objectToBytes(self.node.g ** (self.node.x * r), self.node.group).decode()])