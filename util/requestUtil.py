class urlUtil:
    @staticmethod
    def make_url(addr, port, interface):
        return "http://{addr}:{port}/{interface}".format(addr=addr, port=port, interface=interface)
