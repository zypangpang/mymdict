import configparser,os

class DictConfigs():
    config=configparser.ConfigParser()

    daemon_section="dictionary daemon"
    frontend_section="frontend"

    @classmethod
    def load_configs(cls,file_path):
        cls.config.read(file_path)

    @classmethod
    def get_config(cls,section_name):
        if section_name in cls.config.sections():
            return cls.config[section_name]
        raise Exception(f"No config section {section_name}")

    @classmethod
    def get_value(cls,section,key):
        return cls.config[section][key]

    @classmethod
    def get_daemon_value(cls,key):
        return cls.config[cls.daemon_section][key]
    @classmethod
    def get_frontend_value(cls,key):
        return cls.config[cls.frontend_section][key]

    @classmethod
    def get_dictionary_paths(cls):
        dicts = cls.get_value("dictionary daemon", "dictionaries").split(",")
        dicts=[x.strip() for x in dicts]
        return {os.path.basename(path): path for path in dicts}

    @classmethod
    def get_enabled_dicts(cls):
        try:
            dicts=cls.get_daemon_value("enabled dictionaries").split(",")
        except Exception as e:
            return []
        return [x.strip() for x in dicts]



if __name__ == '__main__':
    print(DictConfigs.get_dictionary_paths())
