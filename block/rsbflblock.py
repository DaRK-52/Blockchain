
sys.path.insert(0, sys.path[0]+"/../")
from block.block import Block

class RSBFLBlock(Block):
    def __init__(self):
        self.previous_hash = ""
        self.nonce = ""
        self.aggregated_model = ""
        self.block_body = ""