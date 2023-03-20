import const
import json
from util import hashTool

# The Base Class of Node should only contains
# (pk, sk) to support p2p communication
class Node():
    def __init__(self, port = DEFAULT_PORT):
        self.public_key = ""
        self.private_key = ""
        self.peer_list = []
        const.ID_CFG_FILE = str(port) + "identity.json" 
    
    def init(self):
        try:
            id_cfg_file = open(const.ID_CFG_FILE, "r")
            id = json.load(id_cfg_file)
            self.public_key = id[const.PUBLIC_KEY]
            self.private_key = id[const.PRIVATE_KEY]
        except FileNotFoundError:
            self.public_key, self.private_key = hashTool.generate_ECDSA_keys()
            id_cfg_file = open(const.ID_CFG_FILE, "w")
            json.dump({
                const.PUBLIC_KEY: self.public_key,
                const.PRIVATE_KEY: self.private_key
            }, id_cfg_file)

# Voting Based Blockchain Node usually needs
# a leader to guide most nodes work
def VotingBasedBlockChainNode(Node):
    def __init__(self, port = DEFAULT_PORT):
        super(VotingBasedBlockChainNode, self).__init__(port = port)
        self.character = ""
        self.leader = {}
        self.election_strategy = {}
        self.consensus_strategy = {}
        self.transaction_pool = {}