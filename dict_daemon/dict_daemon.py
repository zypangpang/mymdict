import constants,logging,os
from dict_daemon.dict_config import DictConfigs
from dict_daemon.build_index import IndexManipulator
from dict_daemon import lookup_utils
from pathlib import Path


class DictDaemon():
    def __init__(self,config_path=None,load_index=True):
        if not config_path:
            config_path=constants.DEFAULT_CONFIG_PATH

        if not os.path.exists(config_path):
            logging.error(f"config file '{config_path}' not exist.")
            logging.error("If this is the first time you run, run 'python mmdict.py init' to init configs.")
            exit(1)

        logging.info("Loading configs... ")
        configs=DictConfigs(config_path)
        self.dictionaries=configs.get_dictionary_paths()
        self.index_prefix=configs.get_daemon_value("index folder")
        self.enabled_dicts=configs.get_enabled_dicts()

        if load_index:
            logging.info("Building indexes... ")
            self._build_indexes()

            logging.info("Loading indexes... ")
            self._load_indexes()


    def _load_indexes(self):
        self.index_obj = IndexManipulator.load_indexes(self.enabled_dicts)

    def _build_indexes(self,rebuild=False,dict_names=None):
        IndexManipulator.index_path_prefix = self.index_prefix
        if not os.path.exists(self.index_prefix):
            logging.info("Index folder not exists. Creating...")
            os.makedirs(self.index_prefix)

        if dict_names:
            dicts={key: self.dictionaries[key] for key in dict_names}
        else:
            dicts=self.dictionaries
        IndexManipulator.build_indexes(dicts,rebuild)

    def rebuild_index(self,dict_names=None):
        self._build_indexes(rebuild=True,dict_names=dict_names)
        self._load_indexes()

    def _lookup(self,word,dict_name):
        if word not in self.index_obj[dict_name]:
            raise Exception(f"No '{word}' entry in {dict_name}")
        index_tuple=self.index_obj[dict_name][word]
        return lookup_utils.decode_record_by_index(self.dictionaries[dict_name], index_tuple)

    def lookup(self,word,dicts=None):
        ans={}
        if not dicts:
            dicts=self.enabled_dicts

        for d in dicts:
            try:
                ans[d]=self._lookup(word,d)
            except Exception as e:
                logging.error(f"Lookup '{word}' in '{d}' failed, error = {e}")
        return ans

    def list_all_words(self,dict_name):
        if dict_name not in self.index_obj:
            raise Exception(f"Unknown dict: {dict_name}")
        return self.index_obj[dict_name].keys()

    def list_dictionaries(self,enabled=True):
        if enabled:
            return {name:str(Path(self.dictionaries[name]).parent) for name in self.enabled_dicts}
        else:
            return self.dictionaries


if __name__ == '__main__':
    daemon=DictDaemon()
    ans=daemon.lookup("write")
    print(ans)

