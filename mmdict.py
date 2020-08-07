import socketserver,json,signal,sys,os
from dict_daemon.dict_daemon import DictDaemon
import daemon,fire
from constants import SOCKET_LOCATION,OS_NAME,HOST,PORT
import log_config,logging

def signal_handler(sig, frame):
    global server
    try:
        server.server_close()
        os.unlink(SOCKET_LOCATION)
    except Exception as e:
        logging.error(e)
    sys.exit(0)

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    dict_daemon=None

    def handle(self):
        self.data = self.request.recv(8192).strip()
        command,extra=self.data.decode("utf-8").split(",")
        if command=="ListWords":
            logging.info(f"List words of {extra} dictionary")
            return_bytes=self.dict_daemon.list_all_words(extra).encode("utf-8")
        elif command=="Lookup":
            logging.info(f"Lookup word '{extra}'")
            definition_list=self.dict_daemon.lookup(extra)
            return_bytes=json.dumps(definition_list).encode("utf-8")
        else:
            logging.info(f"Unknown command {command}")
            return_bytes="Unknown command"

        self.request.sendall(return_bytes)


class Main():
    """
    mmDict
    """
    config_file=None
    @classmethod
    def __run_server(cls):
        global server
        if OS_NAME == "Linux" or OS_NAME=="Darwin":
            if os.path.exists(SOCKET_LOCATION):
                logging.info("mmDict already running")
                logging.info(f"If you are sure mmDict is not running, you can delete {SOCKET_LOCATION} first, "
                      f"then try to run again.")
                exit(0)

            MyTCPHandler.dict_daemon=DictDaemon(cls.config_file)

            # Register signal handler for server cleaning
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            logging.info("running with Unix socket")
            server=socketserver.UnixStreamServer(SOCKET_LOCATION, MyTCPHandler)
            server.serve_forever()

        else:
            MyTCPHandler.dict_daemon=DictDaemon(cls.config_file)
            logging.info("running with TCP socket")
            try:
                server=socketserver.TCPServer((HOST,PORT), MyTCPHandler)
                server.serve_forever()
            except OSError:
                logging.error(f"{HOST}:{PORT} is already in use.")


    @classmethod
    def run(cls,d=False,config_file=None):
        cls.config_file=config_file
        if d:
            logging.info("Run mmDcit in background")
            with daemon.DaemonContext():
                Main.__run_server()
        else:
            Main.__run_server()
    @classmethod
    def rebuild_index(cls,dicts=None):
        dicts=dicts.split(",")
        logging.info(f"Rebuilding index for {dicts}")
        DictDaemon(load_index=False).rebuild_index(dicts)
        logging.info("Done")

    @classmethod
    def init(cls,dict_folder=None):
        pass

    @classmethod
    def import_dict(cls,dict_folder=None):
        pass


if __name__ == "__main__":
    fire.Fire(Main)

