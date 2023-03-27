from flask import Flask, request
from argparse import ArgumentParser
import node

app = Flask(__name__)

@app.route("/broadcast_transaction_handler", method = ["POST"])
def broadcast_transaction_handler():
    msg = json.loads(request.get_data())
    node.broadcast_transaction_handler(msg)
    return const.SUCCESS

@app.route("/broadcast_block_handler", method = ["POST"])
def broadcast_block_handler():
    msg = json.loads(request.get_data())
    node.broadcast_block_handler(msg)
    return const.SUCCESS

@app.route("/build_block", method = ["GET"])
def build_block():
    node.build_block()
    return const.SUCCESS

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', help='host address')
    parser.add_argument('-p', '--port', help='port')
    args = parser.parse_args()

    node = TestNode()
    node.init()
    host = args.address
    port = args.port
    app.run(debug=True, host=host, port=port)