import hashlib
import random
import const

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

def PoWStrategy(CStartegy):
    def __init__(self, node = None):
        self.node = node
        self.difficulty = const.DEFAULT_POW_DIFFICULTY

    def build_block(self):
        block = TestBlock()
        block.block_body = json.dumps(self.node.transaction_pool)
        block.previous_hash = hashlib.sha256(self.node.chain[-1])
        block.nonce = mining()
        return block
    
    def mining(self):
        while True:
            nonce = random.random()
            hash_nonce = int(hashlib.sha256(str(nonce).encode()).hexdigest(), 16)
            if(nonce < ((1 << 255) >> self.difficulty)):
                return nonce

    def check_block(self, block = None):
        if(block.previous_hash != hashlib.sha256(node.chain[-1])):
            return False
        if(int(hashlib.sha256(str(block.nonce).encode()).hexdigest(), 16) >= ((1 << 255) >> self.difficulty)):
            return False
        return True