from xmlrpc.client import ServerProxy

class Client(ServerProxy):
    def __init__(self, address = 'http://localhost', port = 9913):
        super().__init__("{0}:{1}/".format(address, port), allow_none=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)