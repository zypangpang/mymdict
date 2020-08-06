import socketserver,json,signal,sys,os
from dict_daemon import DictDaemon

socket_location="/tmp/mmdict_socket"

def signal_handler(sig, frame):
    server.server_close()
    os.unlink(socket_location)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

daemon=DictDaemon()
class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(8192).strip()
        #print("{} wrote:".format(self.client_address[0]))
        #print(self.data)
        word=self.data.decode("utf-8")
        definition_list=daemon.lookup(word)
        return_bytes=json.dumps(definition_list).encode("utf-8")

        # just send back the same data, but upper-cased
        self.request.sendall(return_bytes)


if __name__ == "__main__":
    #HOST, PORT = "localhost", 9999
    if os.path.exists(socket_location):
        print("Daemon already running")
        exit(0)

    with socketserver.UnixStreamServer(socket_location, MyTCPHandler) as server:
        server.serve_forever()
