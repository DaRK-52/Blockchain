import const
import json
import requests
from transaction import TestTransaction
import random
from strategy import PoWStrategy
from util import hashTool
from block import TestBlock

# The Base Class of Node should only contains
# (pk, sk) to support p2p communication
class Node():
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        self.public_key = ""
        self.private_key = ""
        self.peer_list = []
        self.connected_peer_list = []
        self.transaction_pool = []
        self.consensus_strategy = {}
        self.addr = addr
        self.port = port
        self.chain = []
        self.id_cfg_file = addr + str(port) + "identity.json" 
    
    def init(self):
        self.get_key()
        self.register()
        self.get_peer_list()
        # self.connect_to_peer()

    # get current (pk, sk) from config file
    # if not exist, generate a new pair
    def get_key(self):
        try:
            id_cfg_file = open(self.id_cfg_file, "r")
            id = json.load(id_cfg_file)
            self.public_key = id[const.PUBLIC_KEY]
            self.private_key = id[const.PRIVATE_KEY]
        except FileNotFoundError:
            self.public_key, self.private_key = hashTool.generate_ECDSA_keys()
            id_cfg_file = open(self.id_cfg_file, "w")
            json.dump({
                const.PUBLIC_KEY: self.public_key,
                const.PRIVATE_KEY: self.private_key
            }, id_cfg_file)
    
    # communicate with dns server to register identity
    def register(self):
        url = "http://{dns_host}:{dns_port}/register".format(
            dns_host = const.DEFUALT_DNS_ADDR, 
            dns_port = const.DEFAULT_DNS_PORT
        )
        r = requests.post(url = url, data = json.dumps({
            "addr": self.addr,
            "port": self.port
        }))
        if (r.text == const.SUCCESS):
            return True
        return False

    # communicate with dns server to get peer_list
    def get_peer_list(self):
        url = "http://{dns_host}:{dns_port}/get_peer_list".format(dns_host = const.DEFUALT_DNS_ADDR, dns_port = const.DEFAULT_DNS_PORT)
        r = requests.get(url = url)
        if (r.text != None):
            self.peer_list = json.loads(r.text)
            return True
        return False
    
    # try to connect to peer in the peer list
    def connect_to_peer(self):
        for peer in self.peer_list:
            if (peer["addr"] == self.addr and peer["port"] == self.port):
                continue
            url = "http://{host}:{port}/connect".format(host = peer["addr"], port = peer["port"])
            r = requests.post(url, data = json.dumps({
                "addr": self.addr,
                "port": self.port
            }))
            if (r.text == const.SUCCESS):
                self.connected_peer_list.append(peer)
    
    # decide whether build connection with peer who launch connection
    def connection_from_peer(self, peer):
        if ({"addr": peer["addr"], "port": peer["port"]} not in self.connected_peer_list):
            if (len(self.connected_peer_list) >= const.DEFAULT_PEER_NUM and random.choices([0, 1], weights = (len(self.connected_peer_list), 1))):
                return const.ERROR
            self.connected_peer_list.append(peer)
        return const.SUCCESS

class TestNode(Node):
    def init(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        self.addr = addr
        self.port = port
        self.id_cfg_file = addr + str(port) + "identity.json" 
        super(TestNode, self).init()
        self.consensus_strategy = PoWStrategy(self)
        print(self.consensus_strategy)

    def begin_transaction(self, peer = None):
        transaction = TestTransaction(str(random.random()))
        self.transaction_pool.append(transaction)
        for i in range(len(self.transaction_pool)):
            print(str(self.transaction_pool[i]))
        self.broadcast_transaction(transaction)
    
    def build_block(self):
        block = self.consensus_strategy.build_block()
        self.transaction_pool = [] # clear the transaction pool after building a block(may need change later)
        self.chain.append(block)
        self.broadcast_block(block)

    def broadcast_transaction(self, transaction = None, src_peer = None):
        for peer in self.connected_peer_list:
            if (peer["addr"] == self.addr and peer["port"] == self.port and peer != src_peer):
                continue
            url = "http://{host}:{port}/broadcast_transaction_handler".format(host = peer["addr"], port = peer["port"])
            requests.post(url, data = json.dumps(transaction.__dict__))
    
    def broadcast_block(self, block = None, src_peer = None):
        for peer in self.connected_peer_list:
            if (peer["addr"] == self.addr and peer["port"] == self.port and peer != src_peer):
                continue
            url = "http://{host}:{port}/broadcast_block_handler".format(host = peer["addr"], port = peer["port"])
            requests.post(url, data = json.dumps(block.__dict__))

    def broadcast_transaction_handler(self, transaction = None, environ = None):
        serialized_transaction = TestTransaction("")
        serialized_transaction.msg = transaction["msg"]
        self.transaction_pool.append(serialized_transaction)
        self.broadcast_transaction(serialized_transaction, src_peer = {"addr" : environ["REMOTE_ADDR"], "port" : int(environ["REMOTE_PORT"])})
    
    def broadcast_block_handler(self, block = None, environ = None):
        serialized_block = TestBlock()
        serialized_block.nonce = block["nonce"]
        serialized_block.previous_hash = block["previous_hash"]
        serialized_block.block_body = block["block_body"]
        if(self.consensus_strategy.check_block(serialized_block)):
            self.chain.append(serialized_block)
            self.transaction_pool = []
        self.broadcast_block(serialized_block, src_peer = {"addr" : environ["REMOTE_ADDR"], "port" : int(environ["REMOTE_PORT"])})