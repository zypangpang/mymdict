from dict_parse.mymdict import MDX
import json,zlib,os,logging

class IndexManipulator():

    index_path_prefix=None
    index_obj=None

    @classmethod
    def build_indexes(cls,dict_paths,rebuild=False):
        for name,path in dict_paths.items():
            cls._build_index(name,path,rebuild)

    @classmethod
    def get_index_file_name(cls,dict_name):
        if not cls.index_path_prefix:
            raise Exception("Internal error: index_path_prefix is not set")
        return os.path.join(cls.index_path_prefix,dict_name+".index")

    @classmethod
    def _build_index(cls,dict_name,dict_path,rebuild):
        path=cls.get_index_file_name(dict_name)
        if not rebuild and os.path.exists(path):
            return
        if not os.path.exists(dict_path):
            logging.error(f"{dict_path} not exist")
            return

        logging.info(f"building index for new dictionary {dict_name} ...")

        mdx = MDX(dict_path)
        index_obj = {key: index for key, index in mdx.items()}
        jsonbytes = json.dumps(index_obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        compressed_bytes = zlib.compress(jsonbytes)
        with open(path, "wb") as f:
            f.write(compressed_bytes)

        print(f"building index done")

    @classmethod
    def _load_index(cls,dict_name):
        path=cls.get_index_file_name(dict_name)
        if not os.path.exists(path):
            raise Exception(f"No index file for {dict_name}")
        with open(path, "rb") as f:
            compressed_bytes = f.read()
        decompressed = zlib.decompress(compressed_bytes)
        cls.index_obj[dict_name] = json.loads(decompressed.decode("utf-8"))

    @classmethod
    def load_indexes(cls,dict_names):
        cls.index_obj={}
        for name in dict_names:
            try:
                cls._load_index(name)
            except Exception as e:
                print(e)

        return cls.index_obj


    @classmethod
    def get_index(cls,dict_name):
        if cls.index_obj is None:
            raise Exception("Please load index first")
        return cls.index_obj[dict_name]
