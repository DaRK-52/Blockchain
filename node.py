import const
import json
import requests
import transaction
import random
from util import hashTool

# The Base Class of Node should only contains
# (pk, sk) to support p2p communication
class Node():
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        self.public_key = ""
        self.private_key = ""
        self.peer_list = []
        self.transaction_pool = []
        self.consensus_strategy = {}
        self.addr = addr
        self.port = port
        self.chain = []
        const.ID_CFG_FILE = addr + str(port) + "identity.json" 
    
    def init(self):
        get_key()
        register()
        get_peer_list()

    # get current (pk, sk) from config file
    # if not exist, generate a new pair
    def get_key(self):
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
    
    # communicate with dns server to register identity
    def register(self):
        url = "http://{dns_host}:{dns_port}/register?addr={addr}&port={port}".format(
            dns_host = const.DEFUALT_DNS_ADDR, 
            dns_port = const.DEFAULT_DNS_PORT,
            addr = self.addr,
            port = self.port
        )
        r = requests.get(url = url)
        if (r.text == const.SUCCESS):
            return True
        return False

    # communicate with dns server to get peer_list
    def get_peer_list(self):
        url = "http://{dns_host}:{dns_port}/get_peer_list".format(dns_host = const.DEFUALT_DNS_ADDR, dns_port = const.DEFAULT_DNS_PORT)
        r = requests.get(url = url)
        if (r.status_code == 200):
            self.peer_list = json.loads(r.text)
            return True
        return False 

# Voting Based Blockchain Node usually needs
# a leader to guide most nodes work
class VotingBasedBlockChainNode(Node):
    def __init__(self, port = DEFAULT_PORT):
        super(VotingBasedBlockChainNode, self).__init__(port = port)
        self.character = ""
        self.leader = {}
        self.election_strategy = {}
        self.consensus_strategy = {}
        self.transaction_pool = {}

class TestNode(Node):
    def init(self):
        super(TestNode, self).init()
        self.consensus_strategy = PoWStrategy(self)

    def begin_transaction(self, peer = None):
        transaction = TestTransaction(str(random.random()))
        self.transaction_pool.append(transaction)
        self.broadcast_transaction(transaction)
    
    def generate_block(self):
        block = self.consensus_strategy.build_block()
        self.transaction_pool = [] # clear the transaction pool after building a block(may need change later)
        self.broadcast_block(block)

    def broadcast_transaction(self, transaction = None):
        for peer in peer_list:
            url = "http://{host}:{port}/broadcast_transaction_handler".format(host = peer["addr"], port = peer["port"])
            requests.post(url, data = json.dumps(transaction))
    
    def broadcast_block(self, block = None):
        for peer in peer_list:
            url = "http://{host}:{port}/broadcast_block_handler".format(host = peer["addr"], port = peer["port"])
            requests.post(url, data = json.dumps(block))

    def broadcast_transaction_handler(self, transaction = None):
        self.transaction_pool.append(transaction)
    
    def broadcast_block_handler(self, block = None):
        if(self.consensus_strategy.check_block(block)):
            self.chain.append(block)
            self.transaction_pool = []