import constants
from dict_config import DictConfigs
from build_index import IndexManipulator
import lookup_utils

class DictDaemon():
    def __init__(self,config_path=None):
        if not config_path:
            config_path=constants.DEFAULT_CONFIG_PATH
        DictConfigs.load_configs(config_path)

        self.dictionaries=DictConfigs.get_dictionary_paths()

        IndexManipulator.index_path_prefix=DictConfigs.get_daemon_value("index folder")
        IndexManipulator.build_indexes(self.dictionaries)

        self.enabled_dicts=DictConfigs.get_enabled_dicts()
        self.index_obj=IndexManipulator.load_indexes(self.enabled_dicts)

    def _lookup(self,word,dict_name):
        index_tuple=self.index_obj[dict_name][word]
        return lookup_utils.decode_record_by_index(self.dictionaries[dict_name],index_tuple)

    def lookup(self,word):
        ans=[]
        for d in self.enabled_dicts:
            try:
                ans.append(self._lookup(word,d))
            except Exception as e:
                print(e)

        return ans

if __name__ == '__main__':
    daemon=DictDaemon()
    ans=daemon.lookup("write")
    print(ans)

