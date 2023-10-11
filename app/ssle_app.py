from flask import Flask, request
from argparse import ArgumentParser
import json
import random
import requests
from charm.toolbox.eccurve import prime192v1
from charm.toolbox.ecgroup import ECGroup, G, ZR
from charm.core.engine.util import objectToBytes, bytesToObject
import sys

sys.path.insert(0, sys.path[0] + "/../")
from util.requestUtil import Urlutil
import node.sslenode
import const
import time
import logging

app = Flask(__name__)

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)


# if flag == True, return the dict itself
# in case we need other params
def get_addr_port(flag=False):
    msg = json.loads(request.get_data())
    if (flag):
        return msg["addr"], msg["port"], msg
    return msg["addr"], msg["port"]


@app.route("/connect", methods=["POST"])
def connection_from_peer():
    addr, port = get_addr_port()
    peer = {"addr": addr, "port": port}
    return node.connection_from_peer(peer)


@app.route("/connect_validator", methods=["POST"])
def connection_from_validator():
    addr, port = get_addr_port()
    validator = {"addr": addr, "port": port}
    return node.connection_from_validator(validator)


@app.route("/broadcast_shared_list_handler", methods=["POST"])
def broadcast_shared_list_handler():
    shared_list = json.loads(request.get_data())
    print("From handler:", sys.getsizeof(json.dumps(shared_list)))
    if len(shared_list) > len(node.election_strategy.shared_list) or len(shared_list) == len(
            node.election_strategy.validator_list):
        node.election_strategy.shared_list = shared_list
    else:
        return const.SUCCESS
    node.begin_election()

    return const.SUCCESS


@app.route("/broadcast_group_primitive_handler", methods=["POST"])
def broadcast_group_primitive_handler():
    node.election_strategy.g = bytesToObject(json.loads(request.get_data()).encode(), node.election_strategy.group)
    return const.SUCCESS


@app.route("/broadcast_identity_handler", methods=["POST"])
def broadcast_identity_handler():
    addr, port, msg = get_addr_port(flag=True)
    x = bytesToObject(msg["x"].encode(), node.election_strategy.group)
    url = Urlutil.make_url(const.DEFUALT_DNS_ADDR, const.DEFAULT_DNS_PORT, "get_random_number_ssle")
    r = requests.get(url=url)
    node.election_strategy.leader_index = int(r.text)
    if node.check_leader(x=x):
        print("get identity from other nodes!")
        node.election_strategy.round = node.election_strategy.round + 1
        node.election_strategy.leader = {"addr": addr, "port": port}
        return const.SUCCESS
    return const.ERROR


@app.route("/begin_election", methods=["GET"])
def begin_election():
    node.begin_election()
    return const.SUCCESS


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', help='host address')
    parser.add_argument('-p', '--port', help='port')
    args = parser.parse_args()

    node = node.sslenode.SSLENode()
    node.init(addr=args.address, port=args.port)
    host = args.address
    port = args.port
    app.run(debug=False, host=host, port=port)
