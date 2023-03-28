import hashlib
import random
import const
from block import TestBlock
import json

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