sys.path.insert(0, sys.path[0]+"/../")
from transaction.transaction import Transaction

class RSBFLTransaction(Transaction):
    def __init__(self, msg = None):
        self.msg = msg
        self.local_update = ""
        self.uploader = ""