from flask import Flask, request
import const
import json
import numpy as np

app = Flask(__name__)

# dns server records all peer who connects
# to it, (ip, port) is the identifier
# TODO: persistance or addr check
@app.route("/register", methods = ["GET"])
def register():
    addr = request.environ["REMOTE_ADDR"]
    port = request.environ["REMOTE_PORT"]
    
    if (port == None or addr == None):
        return const.ERROR
    if ({"addr":addr, "port":port} not in peer_list):
        peer_list.append({"addr":addr, "port":port})
    return const.SUCCESS

@app.route("/get_peer_list", methods = ["GET"])
def get_peer_list():
    if (len(peer_list) >= const.DEFAULT_PEER_NUM):
        return json.dumps(list(np.random.choice(peer_list, const.DEFAULT_PEER_NUM, replace = False)))
    return json.dumps(peer_list)

@app.route("/register_as_validator", methods = ["GET"])
def register_as_validator():
    # TODO: A PoW solution of identity
    addr = request.environ["REMOTE_ADDR"]
    port = request.environ["REMOTE_PORT"]

    if (port == None or addr == None):
        return const.ERROR
    if ({"addr":addr, "port":port} not in validator_list):
        validator_list.append({"addr":addr, "port":port})
    # when registration succeed, return the index of the validator which will be used in ssle
    return len(validator_list)

@app.route("/get_validator_list", methods = ["GET"])
def get_validator_list():
    return json.dumps(validator_list)

if (__name__ == "__main__"):
    peer_list = []
    validator_list = []
    app.run(debug = True, host = const.DEFUALT_DNS_ADDR, port = const.DEFAULT_DNS_PORT)