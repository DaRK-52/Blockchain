class Urlutil:
    @staticmethod
    def make_url(addr, port, interface):
        return "http://{addr}:{port}/{interface}".format(addr=addr, port=port, interface=interface)


class Datautil:
    @staticmethod
    def make_addr_port_dict(node):
        return {"addr": node.addr, "port": node.port}
