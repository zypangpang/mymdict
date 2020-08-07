import configparser,os

class DictConfigs():
    daemon_section = "dictionary daemon"
    frontend_section = "frontend"

    def __init__(self,file_path):
        self.config=configparser.ConfigParser()
        self.config.read(file_path)

    def get_config(self,section_name):
        if section_name in self.config.sections():
            return self.config[section_name]
        raise Exception(f"No config section {section_name}")

    def get_value(self, section, key):
        return self.config[section][key]

    def get_daemon_value(self, key):
        return self.config[self.daemon_section][key]

    def get_frontend_value(self, key):
        return self.config[self.frontend_section][key]

    def get_dictionary_paths(self):
        dicts = self.get_value("dictionary daemon", "dictionaries").split(",")
        dicts=[x.strip() for x in dicts]
        return {os.path.basename(path): path for path in dicts}

    def get_enabled_dicts(self):
        try:
            dicts=self.get_daemon_value("enabled dictionaries").split(",")
        except Exception as e:
            return []
        return [x.strip() for x in dicts]



if __name__ == '__main__':
    pass
