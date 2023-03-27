import hashlib

class Strategy():
    pass

class EStrategy(Strategy):
    pass

class CStartegy(Strategy):
    def __init__(self, node = None):
        self.node = node
    
    def build_block(self):
        pass

def PoWStrategy(CStartegy):
    def build_block(self):
        block = TestBlock()
        block.block_body = json.dumps(self.node.transaction_pool)
        block.nonce = mining()
    
    def mining(self):
        self.difficulty = 1
        while True:
            nonce = int(hashlib.sha256(str(random.random()).encode()).hexdigest(), 16)
            if(nonce < ((1 << 255) >> self.difficulty)):
                return nonce