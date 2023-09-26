from flask import Flask, request
import const
import json
import numpy as np
import random

app = Flask(__name__)

def get_requester_addr(request_data):
    msg = json.loads(request_data)
    return msg["addr"], msg["port"]

def append_registration_list(addr, port, list):
    if (port == None or addr == None):
        raise ValueError("Invalid address or port.")
    if ({"addr":addr, "port":port} not in list):
        list.append({"addr":addr, "port":port})

# dns server records all peer who connects
# to it, (ip, port) is the identifier
# TODO: persistance or addr check
@app.route("/register", methods = ["POST"])
def register():
    addr, port = get_requester_addr(request.get_data())
    try:
        append_registration_list(addr, port, peer_list)
    except ValueError as e:
        return const.ERROR
    
    return const.SUCCESS

@app.route("/get_peer_list", methods = ["GET"])
def get_peer_list():
    return json.dumps(peer_list)

@app.route("/register_as_validator", methods = ["POST"])
def register_as_validator():
    addr, port = get_requester_addr(request.get_data())
    try:
        append_registration_list(addr, port, validator_list)
    except ValueError as e:
        return const.ERROR
    
    # when registration succeed, return the index of the validator which will be used in ssle
    return str(len(validator_list))

@app.route("/get_validator_list", methods = ["GET"])
def get_validator_list():
    return json.dumps(validator_list)

@app.route("/get_random_number_ssle", methods = ["GET"])
def get_random_number_ssle():
    return "1"

if (__name__ == "__main__"):
    peer_list = []
    validator_list = []
    counter = 0
    r = -1
    app.run(debug = True, host = const.DEFUALT_DNS_ADDR, port = const.DEFAULT_DNS_PORT)