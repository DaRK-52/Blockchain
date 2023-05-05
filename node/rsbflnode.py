from torchvision import datasets, transforms
import numpy as np
import json
import hashlib

sys.path.insert(0, sys.path[0]+"/../")
from node.sslenode import SSLENode
from utils.sampling import mnist_iid, mnist_noniid, cifar_iid
from utils.options import args_parser
from utils.serialization import translate_json_to_model, translate_model_to_json
from models.Update import LocalUpdate
from models.Nets import MLP, CNNMnist, CNNCifar
from models.Fed import FedAvg, MultiKrum
from models.test import test_img
from block.rsbflblock import RSBFLBlock
import const
from strategy.pbft import PBFTStrategy

class ValidatorNode(SSLENode):
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        super(RSBFLNode, self).init()
        self.consensus_strategy = PBFTStrategy(self)
        self.local_update_pool = []
        self.blockchain = []

    def build_block(self):
        if (self.check_leader(self.x)):
            block = RSBFLBlock()
            block.previous_hash = hashlib.sha256(str(elf.blockchain[-1]).encode()).hexdigest()
            block.aggregated_model = self.aggregate_model()
            block.block_body = self.local_update_pool # TODO
            self.broadcast_block_to_validator(block)

    def aggregate_model(self):
        return MultiKrum(self.local_update_pool)

    def broadcast_local_update_handler(self, msg):
        local_update = translate_json_to_model(msg)
        self.local_update_pool.append(local_update)

    # consensus
    def broadcast_block_to_validator(self, block):
        counter = 1
        for validator in self.validator_list:
            if (validator["addr"] == self.addr and validator["port"] == self.port):
                continue
            url = "http://{host}:{port}/broadcast_block_to_validator_handler".format(host = validator["addr"], port = validator["port"])
            r = requests.post(url, data = block)
            if (r.text == const.SUCCESS):
                counter = counter + 1
        if (counter > len(self.validator_list) * 3 / 2):
            self.blockchain.append(block)
            self.broadcast_block(block)
    
    # confirmation
    def broadcast_block(self, block):
        for validator in self.validator_list:
            if (validator["addr"] == self.addr and validator["port"] == self.port):
                continue
            url = "http://{host}:{port}/broadcast_block_handler".format(host = validator["addr"], port = validator["port"])
            requests.post(url, data = block)
        
        for peer in self.peer_list:
            url = "http://{host}:{port}/broadcast_block_handler".format(host = peer["addr"], port = peer["port"])
            requests.post(url, data = block)

    def broadcast_block_to_validator_handler(self):
        pass
    
    def broadcast_block_handler(self, block):
        self.blockchain.append(block)


class TrainerNode(Node):
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        super(TrainerNode, self).init()
        self.prepare_training()
        self.get_validator_list()
        self.blockchain = []

    def prepare_training(self):
        trans_cifar = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        self.args = args_parser()
        self.args.device = torch.device('cuda:{}'.format(args.gpu) if torch.cuda.is_available() and args.gpu != -1 else 'cpu')
        self.dataset_train = datasets.CIFAR10('../data/cifar', train=True, download=True, transform=trans_cifar)
        self.dataset_test = datasets.CIFAR10('../data/cifar', train=False, download=True, transform=trans_cifar)
        self.dict_users = cifar_iid(dataset_train, args.num_users)
        self.net_glob = CNNCifar(args=self.args).to(self.args.device)
        self.w_glob = self.net_glob.state_dict()
        self.idx = np.random.randint(self.args.num_users)

    def get_validator_list(self):
        url = "http://{dns_host}:{dns_port}/get_validator_list".format(dns_host = const.DEFUALT_DNS_ADDR, dns_port = const.DEFAULT_DNS_PORT)
        r = requests.get(url = url)
        if (r.text != None):
            self.validator_list = json.loads(r.text)
            return True
        return False
    
    def train(self):
        loss_train = []
        cv_loss, cv_acc = [], []
        val_loss_pre, counter = 0, 0
        net_best = None
        best_loss = None
        val_acc_list, net_list = [], []

        local = LocalUpdate(args = self.args, dataset = self.dataset_train, idxs = self.dict_users[self.idx])
        self.w, self.loss = local.train(net = copy.deepcopy(self.net_glob).to(args.device))

    def broadcast_local_update(self):
        for validator in self.validator_list:
            url = "http://{host}:{port}/connect_validator".format(host = validator["addr"], port = validator["port"])
            requests.port(url, data = translate_model_to_json(self.w.state_dict()))
    
    def broadcast_block_handler(self, block):
        self.blockchain.append(block)

# Requester need to be the last one register in the network
class RequesterNode(Node):
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        super(RequesterNode, self).init()
    
    def broadcast_init_block(self):
        # get init model
        args = args_parser()
        net_glob = CNNCifar(args = args).to(args.device)
        w_glob = net_glob.state_dict()
        w_glob = translate_model_to_json(w_glob)

        init_block = RSBFLBlock()
        init_block.previous_hash = const.GENISIS_BLOCK
        init_block.aggregated_model = w_glob
        for peer in peer_list:
            if (peer["addr"] == self.addr and peer["port"] == self.port):
                continue
            url = "http://{host}:{port}/broadcast_init_block_handler".format(host = peer["addr"], port = peer["port"])
            requests.post(url, data = json.dumps(init_block))
