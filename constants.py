import platform
from enum import Enum
from pathlib import Path
OS_NAME=platform.system()

DEFAULT_CONFIG_PATH=Path.home().joinpath(".mmdict/configs.ini")
SOCKET_LOCATION = "/tmp/mmdict_socket"
HOST,PORT="localhost",9999

DEBUG=True

CONFIG_DAEMON_SECTION = "dictionary daemon"
CONFIG_FRONTEND_SECTION= "frontend"

ENCODINGS = ['utf-8', 'gb18030', 'utf-16']
SOUND_PLAYER='mpv'
class FRONT_END(Enum):
    QTWEBENGINE=1
    CONSOLE=2
if __name__ == '__main__':
    print(DEFAULT_CONFIG_PATH)

