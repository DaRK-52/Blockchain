class Block:
    pass

class TestBlock(Block):
    def __init__(self):
        self.nonce = ""
        self.previous_hash = ""
        self.block_body = ""