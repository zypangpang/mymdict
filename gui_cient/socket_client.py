import socket,json,constants
from enum import Enum
from bs4 import BeautifulSoup

class FRONT_END(Enum):
    QTWEBENGINE=1
    CONSOLE=2
class SocketClient():
    front_end=FRONT_END.QTWEBENGINE
    @classmethod
    def __request(cls, data):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(constants.SOCKET_LOCATION)
            sock.sendall(data.encode("utf-8"))
            msg_list = []
            while True:
                msg = sock.recv(8192)
                if not msg:
                    break
                msg_list.append(msg)
        return b"".join(msg_list).decode("utf-8")

    @classmethod
    def __tweak_for_qt_webengine(cls,result_obj):
        for key,val in result_obj.items():
            soup=BeautifulSoup(val,"lxml")
            all_a=soup.find_all("a")
            for a in all_a:
                if " " in a.get('href',""):
                    a['href']=a['href'].replace("://",":")
            result_obj[key]=str(soup)
        return result_obj

    @classmethod
    def __tweak_for_console(cls, result_obj):
        return result_obj

    @classmethod
    def lookup(cls,word,dicts=None):
        data = f"Lookup:{word}"
        if dicts:
            data=data+","+','.join(dicts)
        recv_data=cls.__request(data)
        r_obj=json.loads(recv_data)
        if cls.front_end==FRONT_END.QTWEBENGINE:
            return cls.__tweak_for_qt_webengine(r_obj)
        elif cls.front_end==FRONT_END.CONSOLE:
            return cls.__tweak_for_console(r_obj)
        return r_obj


    @classmethod
    def list_dicts(cls,enabled=True):
        data=f"ListDicts:{int(enabled)}"
        return json.loads(cls.__request(data))

    @classmethod
    def list_words(cls,dict_name):
        data=f"ListWord:{dict_name.strip()}"
        return cls.__request(data).split(',')




if __name__ == '__main__':
    pass


