from flask import Flask, request
from argparse import ArgumentParser
import node
import json
import const

app = Flask(__name__)

@app.route("/broadcast_transaction_handler", methods = ["POST"])
def broadcast_transaction_handler():
    msg = json.loads(request.get_data())
    node.broadcast_transaction_handler(msg)
    return const.SUCCESS

@app.route("/broadcast_block_handler", methods = ["POST"])
def broadcast_block_handler():
    msg = json.loads(request.get_data())
    node.broadcast_block_handler(msg)
    return const.SUCCESS

@app.route("/build_block", methods = ["GET"])
def build_block():
    node.build_block()
    return const.SUCCESS

@app.route("/print_block", methods = ["GET"])
def print_block():
    msg = ""
    for block in node.chain:
        msg += "nonce: {}\nprevious_hash: {}\nblock_body: {}\n".format(str(block.nonce), block.previous_hash, block.block_body)
    return msg

@app.route("/begin_transaction", methods = ["GET"])
def begin_transaction():
    node.begin_transaction()
    return const.SUCCESS

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', help='host address')
    parser.add_argument('-p', '--port', help='port')
    args = parser.parse_args()

    node = node.TestNode()
    node.init(addr = args.address, port = args.port)
    host = args.address
    port = args.port
    app.run(debug=True, host=host, port=port)