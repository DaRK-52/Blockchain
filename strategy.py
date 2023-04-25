import hashlib
import random
import const
from block import TestBlock
import json
from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject

class Strategy():
    pass

class EStrategy(Strategy):
    pass

class CStartegy(Strategy):
    def __init__(self, node = None):
        self.node = node
    
    def build_block(self):
        pass
    
    def check_block(self):
        pass

class PoWStrategy(CStartegy):
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
            self.node.g = self.group.random(G)
            self.node.broadcast_group_primitive()

        r = self.node.group.random(ZR)
        self.node.x = self.node.group.random(ZR)
        self.node.shared_list.append([objectToBytes(self.node.g ** r).decode(), objectToBytes(self.node.g ** (self.node.x * r)).decode()])
        self.shuffle()
        self.node.broadcast_shared_list()
    
    # The elected leader substitute its secret
    def incre_election(self):
        if (self.check_leader()):
            pass
    
    # Every time we start ssle, we need to blind and shuffle the list
    def shuffle():
        # TODO: blind the list
        temp_list = []
        r = self.node.group.random(ZR)
        for item in self.node.shared_list:
            u = bytesToObject(item[0].encode())
            v = bytesToObject(item[1].encode())
            temp_list.append([objectToBytes(u ** r).decode(), objectToBytes(v ** r).decode()])
        self.node.shared_list = temp_list
        random.shuffle(self.node.shared_list)
    
    def check_leader(self, x = None):
        if (x == None):
            x = self.node.x
        u = bytesToObject(self.node.shared_list[self.node.leader_index][0].encode())
        v = bytesToObject(self.node.shared_list[self.node.leader_index][1].encode())
        if (u ** x == v):
            return True
        return False