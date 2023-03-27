from flask import Flask, request
import const
import json

app = Flask(__name__)

# dns server records all peer who connects
# to it, (ip, port) is the identifier
# TODO: persistance or addr check
@app.route("/register", methods = ["GET"])
def register():
    addr = request.args.get(const.ADDR)
    port = request.args.get(const.PORT)
    
    if (port == None or addr == None):
        return const.ERROR
    if ([addr, port] not in peer_list):
        peer_list.append(["addr":addr, "port":port])
    
    return const.SUCCESS

@app.route("/get_peer_list", methods = ["GET"])
def get_peer_list():
    return json.dumps(peer_list)

if (__name__ == "__main__"):
    peer_list = []
    app.run(debug = True, host = const.DEFUALT_DNS_ADDR, port = const.DEFAULT_DNS_PORT)