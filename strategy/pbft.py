

sys.path.insert(0, sys.path[0]+"/../")
from strategy.strategy import CStrategy

class PBFTStrategy(CStrategy):
    def __init__(self, node = None):
        self.node = node
        self.counter = {}

    def build_block(self):
        pass
    
    # don
    def check_block(self, block = None):
        pass

    def 