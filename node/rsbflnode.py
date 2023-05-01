from torchvision import datasets, transforms
import numpy as np
import json

sys.path.insert(0, sys.path[0]+"/../")
from node.sslenode import SSLENode
from utils.sampling import mnist_iid, mnist_noniid, cifar_iid
from utils.options import args_parser
from models.Update import LocalUpdate
from models.Nets import MLP, CNNMnist, CNNCifar
from models.Fed import FedAvg
from models.test import test_img

class ValidatorNode(SSLENode):
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        super(RSBFLNode, self).init()

    

class TrainerNode(Node):
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        super(TrainerNode, self).init()
        self.prepare_training()
        self.get_validator_list()

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

class RequesterNode(Node):
    def __init__(self, addr = const.DEFAULT_ADDR, port = const.DEFAULT_PORT):
        super(RequesterNode, self).init()
    
    def broadcast_init_model(self):
        args = args_parser()
        net_glob = CNNCifar(args = args).to(args.device)
        w_glob = net_glob.state_dict()
        for entry in w_glob:
            w_glob[entry] = w_glob[entry].cpu().data.numpy().tolist()
        json.dumps(w_glob)
