from flask import Flask, request
from argparse import ArgumentParser
import sslenode
import json
import const
import random

app = Flask(__name__)

@app.route("/connect", methods = ["GET"])
def connection_from_peer():
    addr = request.environ["REMOTE_ADDR"]
    port = request.environ["REMOTE_PORT"]
    peer = ["addr": addr, "port": port]
    return node.connection_from_peer(peer)

@app.route("/connect_validator", methods = ["GET"])
def connection_from_validator():
    addr = request.environ["REMOTE_ADDR"]
    port = request.environ["REMOTE_PORT"]
    validator = ["addr": addr, "port": port]
    return node.connection_from_validator(validator)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', help='host address')
    parser.add_argument('-p', '--port', help='port')
    args = parser.parse_args()

    node = sslenode.SSLENode()
    node.init(addr = args.address, port = args.port)
    host = args.address
    port = args.port
    app.run(debug=True, host=host, port=port)