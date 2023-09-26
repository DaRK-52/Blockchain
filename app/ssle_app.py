from flask import Flask, request
from argparse import ArgumentParser
import json
import random
import requests
from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject
import sys
sys.path.insert(0, sys.path[0]+"/../")
import node.sslenode
import const
import time

app = Flask(__name__)

# if flag == True, return the dict itself
# in case we need other params
def get_addr_port(flag = False):
    msg = json.loads(request.get_data())
    if (flag):
        return msg["addr"], msg["port"], msg
    return msg["addr"], msg["port"]

@app.route("/connect", methods = ["POST"])
def connection_from_peer():
    addr, port = get_addr_port()
    peer = {"addr": addr, "port": port}
    return node.connection_from_peer(peer)

@app.route("/connect_validator", methods = ["POST"])
def connection_from_validator():
    addr, port = get_addr_port()
    validator = {"addr": addr, "port": port}
    return node.connection_from_validator(validator)

@app.route("/broadcast_shared_list_handler", methods = ["POST"])
def broadcast_shared_list_handler():
    shared_list = json.loads(request.get_data())
    print("List length: " + str(len(shared_list)))
    if len(shared_list) > len(node.shared_list) or len(shared_list) == len(node.validator_list):
        node.shared_list = shared_list
    else:
        # TODO: just a try
        return const.SUCCESS
    node.begin_election()
    
    # ask dns server for the random number
    if len(node.shared_list) == len(node.validator_list):
        print("start validating")
        print(node.shared_list)
        node.has_leader = True
        url = "http://{dns_host}:{dns_port}/get_random_number_ssle".format(dns_host = const.DEFUALT_DNS_ADDR, dns_port = const.DEFAULT_DNS_PORT)
        r = requests.get(url = url)
        node.leader_index = int(r.text)
        print(node.check_leader())
        if (node.check_leader()):
            node.leader = {"addr": node.addr, "port": node.port}
            print(node.addr + ":" + node.port)
            print(time.time())
            print("I'm the leader1!")
            node.broadcast_identity()
    return const.SUCCESS

@app.route("/broadcast_group_primitive_handler", methods = ["POST"])
def broadcast_group_primitive_handler():
    node.g = bytesToObject(json.loads(request.get_data()).encode(), node.group)
    return const.SUCCESS

@app.route("/broadcast_identity_handler", methods = ["POST"])
def broadcast_identity_handler():
    addr, port, msg = get_addr_port(flag = True)
    x = bytesToObject(msg["x"].encode(), node.group)
    if (node.check_leader(x = x)):
        node.leader = {"addr": addr, "port": port}
        return const.SUCCESS
    return const.ERROR

@app.route("/begin_election", methods = ["GET"])
def begin_election():
    print(time.time())
    node.begin_election()
    return const.SUCCESS

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', help='host address')
    parser.add_argument('-p', '--port', help='port')
    args = parser.parse_args()

    node = node.sslenode.SSLENode()
    node.init(addr = args.address, port = args.port)
    host = args.address
    port = args.port
    app.run(debug=True, host=host, port=port)