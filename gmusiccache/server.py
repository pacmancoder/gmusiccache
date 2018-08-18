from xmlrpc.server import SimpleXMLRPCServer as BaseXMLRPCServer


class Server:
    def __init__(self, service, port = 9913):
        """
        Initialize server

        :param service: class which provides service
        :param port: port to start service on. default is 9913
        """

        self.__service = service
        self.__port = port

    def run(self):
        """
        Run server
        """

        with BaseXMLRPCServer(('localhost', int(self.__port)), allow_none=True) as xmlrpc_server:
            xmlrpc_server.register_introspection_functions()

            for fn in self.__service.get_api():
                xmlrpc_server.register_function(fn)

            xmlrpc_server.serve_forever()