import socketserver,json,signal,sys,os
from dict_daemon.dict_daemon import DictDaemon,DictConfigs
import daemon,fire,constants
import log_config,logging,configparser
from pathlib import Path

def signal_handler(sig, frame):
    global server
    try:
        server.server_close()
        os.unlink(constants.SOCKET_LOCATION)
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
        command,extra=self.data.decode("utf-8").split(":")
        try:
            return_str=getattr(self,command)(extra)
        except AttributeError:
            return_str=f'Unknown command {command}'.encode("utf-8")
        except Exception as e:
            return_str=str(e)
        self.request.sendall(return_str.encode("utf-8"))

    def ListWord(self,dict_name):
        logging.info(f"List words of {dict_name} dictionary")
        return self.dict_daemon.list_all_words(dict_name)

    def Lookup(self,extra):
        param_list=extra.split(",")
        word=param_list[0]
        dicts=param_list[1:]
        logging.info(f"Lookup word {word} in {dicts if dicts else 'enabled dicts'}")
        definition_list = self.dict_daemon.lookup(word,dicts)
        return json.dumps(definition_list)

    def ListDicts(self,extra):
        logging.info("List dictionaries")
        enabled=extra if extra else 1
        return '\n'.join(self.dict_daemon.list_dictionaries(enabled))



class Main():
    """
    mmDict: A simple mdict lookup daemon
    """
    __config_file=None

    @classmethod
    def __run_server(cls):
        global server
        if constants.OS_NAME == "Linux" or constants.OS_NAME=="Darwin":
            if os.path.exists(constants.SOCKET_LOCATION):
                logging.info("mmDict already running")
                logging.info(f"If you are sure mmDict is not running, you can delete {constants.SOCKET_LOCATION} first, "
                      f"then try to run again.")
                exit(0)

            MyTCPHandler.dict_daemon=DictDaemon(cls.__config_file)

            # Register signal handler for server cleaning
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            logging.info("running with Unix socket")
            server=socketserver.UnixStreamServer(constants.SOCKET_LOCATION, MyTCPHandler)
            server.serve_forever()

        else:
            MyTCPHandler.dict_daemon=DictDaemon(cls.__config_file)
            logging.info("running with TCP socket")
            try:
                server=socketserver.TCPServer((constants.HOST,constants.PORT), MyTCPHandler)
                server.serve_forever()
            except OSError:
                logging.error(f"{constants.HOST}:{constants.PORT} is already in use.")


    @classmethod
    def run(cls,d=False,config_file=None):
        """
        run mmDict server
        :param d: run as daemon process
        :param config_file: Optional. custom config file path.
        """
        cls.__config_file=config_file
        if d:
            logging.info("Run mmDcit in background")
            with daemon.DaemonContext():
                Main.__run_server()
        else:
            Main.__run_server()

    @classmethod
    def rebuild_index(cls,dicts=None):
        '''
        Rebuild dictionary indexes
        :param dicts: Optional. dicts for rebuilding index
        '''
        dicts=dicts.split(",")
        logging.info(f"Rebuilding index for {dicts}")
        DictDaemon(load_index=False).rebuild_index(dicts)
        logging.info("Done")


    @classmethod
    def init(cls,dict_folder=None):
        '''
        Init configs. You need to run this command the first time you use mmDict.
        :param dict_folder: Optional. If given, import dictionaries in dict_folder at the same time.
        '''
        if constants.DEFAULT_CONFIG_PATH.exists():
            logging.info(f"Config file {constants.DEFAULT_CONFIG_PATH} already exists")
            logging.info("Exit.")
        else:
            os.makedirs(constants.DEFAULT_CONFIG_PATH.parent, 0o0755)
            DictConfigs.generate_init_configs()
            logging.info(f"Init config file generated as {constants.DEFAULT_CONFIG_PATH}")
            logging.info("Change 'dictionaries' and 'enabled dictionaries' field to add your dictionaries or "
                         "run 'python mmdict import <folder>' to import dictionaries")
            if dict_folder:
                cls.import_dict(dict_folder)
                logging.info("Import dictionaries success")


    @classmethod
    def import_dict(cls,dict_folder,config_path=None):
        '''
        Import dictionaries from dict_folder. This will overwrite original settings in mmDict config file.
        :param config_path: Optional. update settings in custom config_path
        '''
        if not config_path:
            config_path=constants.DEFAULT_CONFIG_PATH
        configs=DictConfigs(config_path)
        dict_folder=Path(dict_folder)
        dicts=[str(x.absolute()) for x in dict_folder.iterdir() if x.is_file() and x.suffix == '.mdx']
        names=configs.set_dicts(dicts)
        logging.info(f"Imported {len(names)} dictionaries: {names}")

    @classmethod
    def add_dict(cls,mdx_path,config_path=None):
        '''
        Add dict to config file
        :param mdx_path: dictionary mdx file path
        :param config_path: Optional. update settings in custom config_path
        '''
        if not config_path:
            config_path=constants.DEFAULT_CONFIG_PATH
        configs=DictConfigs(config_path)
        name=configs.add_dict(mdx_path)
        logging.info(f"Added dictionary {name}")

    @classmethod
    def list_dicts(cls,enabled=True):
        """
        List dictionaries
        :param enabled: Only list enabled dicts or all dicts. Default True
        """
        print('\n'.join(DictDaemon(constants.DEFAULT_CONFIG_PATH,False).list_dictionaries(enabled)))


if __name__ == "__main__":
    fire.Fire(Main)

