import  logging
import PyQt5.QtWidgets as Widgets
from PyQt5.QtCore import QUrl, QTextStream, QByteArray, QIODevice,Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo, QWebEngineUrlSchemeHandler, \
    QWebEngineUrlScheme
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEnginePage, QWebEngineProfile
from PyQt5 import QtWebEngineWidgets, QtCore
from .socket_client import SocketClient
from .gui_utils import set_default_font,join_dict_results,pretty_dict_result

class MyUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:
        print("aaa")
        print(info.requestUrl())

class EntrySchemeHandler(QWebEngineUrlSchemeHandler):
    def requestStarted(self, request):
        url = request.requestUrl()
        _,item = url.toString().split(":")
        item=item.strip("/ ")
        result_obj: dict = SocketClient.lookup(item)
        raw_html=join_dict_results(result_obj).encode("utf-8")
        buf = QtCore.QBuffer(request)
        #request.destroyed.connect(buf.deleteLater)
        buf.open(QtCore.QIODevice.WriteOnly)
        buf.write(raw_html)
        buf.seek(0)
        buf.close()
        request.reply(b"text/html", buf)

class MyWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url: QUrl, type: QWebEnginePage.NavigationType, isMainFrame: bool, **kwargs):
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            _, item = url.toString().split(":")
            item = item.strip("/ ")
            dict_name=MainWindow.dictionaries[MainWindow.dict_index-1][0]
            result_obj: dict = SocketClient.lookup(item,[dict_name])
            raw_html = pretty_dict_result(dict_name,result_obj[dict_name])
            #print(self.url())
            self.setHtml(raw_html,self.url())
            MainWindow.history.append(item)
            return False

        return True

ENTRY_SCHEME=b"entry"

class MainWindow(Widgets.QWidget):
    dict_index = 0
    result_obj = {}
    dictionaries=[]
    history=[]

    def __init__(self):
        super().__init__()

        self.zoom_factor=1
        self.init_dictionary()

        #self.app=Widgets.QApplication([])
        #self.window = Widgets.QWidget()

        QWebEngineUrlScheme.registerScheme(QWebEngineUrlScheme(ENTRY_SCHEME))

        self.line_edit=Widgets.QLineEdit("Type word here")
        self.search_button=Widgets.QPushButton('&Search')
        self.status_bar=Widgets.QStatusBar()
        self.back_btn=Widgets.QPushButton('Back')
        self.next_btn=Widgets.QPushButton("Next")

        self.init_webview()


        self.init_layout()

        self.connect_slot()

        self.show()

    def init_dictionary(self):
        try:
            MainWindow.dictionaries=SocketClient.list_dicts()
        except Exception as e:
            logging.error(e)
            logging.error("It seems the mmdict daemon is not running. Please first run the daemon.")
            exit(1)

    def init_layout(self):
        layout = Widgets.QVBoxLayout()
        Hlayout = Widgets.QHBoxLayout()
        Hlayout.addWidget(self.line_edit)
        Hlayout.addWidget(self.search_button)
        Hlayout.addWidget(self.back_btn)
        Hlayout.addWidget(self.next_btn)
        layout.addLayout(Hlayout)
        layout.addWidget(self.view)
        self.status_bar.setFixedHeight(20)
        layout.addWidget(self.status_bar)
        #layout.setSpacing(0)
        layout.setContentsMargins(3,3,3,3)
        self.setLayout(layout)
        self.setMinimumHeight(700)
        self.setMinimumWidth(700)

    def init_webview(self):
        set_default_font("Noto Sans CJK SC",16)


        self.profile=QWebEngineProfile.defaultProfile()
        #handler = self.profile.urlSchemeHandler(ENTRY_SCHEME)
        #if handler is not None:
        #    self.profile.removeUrlSchemeHandler(handler)

        self.handler=EntrySchemeHandler()
        self.profile.installUrlSchemeHandler(ENTRY_SCHEME,self.handler)
        self.page = MyWebPage(self.profile)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setPage(self.page)
        style="""
        @keyframes example {
  0%   {color:red; left:50px; top:50px;}
  25%  {color:yellow; left:250px; top:50px;}
  50%  {color:blue; left:250px; top:450px;}
  75%  {color:green; left:50px; top:450px;}
  100% {color:red; left:50px; top:50px;}
}
h1 {
animation-name: example; 
animation-duration: 4s;
position:relative;
animation-iteration-count: 2;
display: table;
left: 50px;
top:50px;
}
        """

        self.page.setHtml(f'<style>{style}</style><h1>:-)<br>Welcome to mmDict</h1>')

        #self.interceptor=MyUrlRequestInterceptor()
        #self.profile.setUrlRequestInterceptor(self.interceptor)

    def connect_slot(self):
        self.search_button.clicked.connect(self.lookup)
        self.page.linkHovered.connect(self.showMessage)
        self.back_btn.clicked.connect(self.history_back)
        self.next_btn.clicked.connect(self.show_next_dict)
        Widgets.QShortcut(QKeySequence(Qt.Key_Return),self.line_edit).activated.connect(self.lookup)
        Widgets.QShortcut(QKeySequence.ZoomIn,self.view).activated.connect(self.zoomIn)
        Widgets.QShortcut(QKeySequence.ZoomOut,self.view).activated.connect(self.zoomOut)


    def history_back(self):
        if len(MainWindow.history) >=2:
            self.lookup(MainWindow.history[-2])
            MainWindow.history.pop()

    def zoomIn(self):
        self.zoom_factor+=.1
        self.page.setZoomFactor(self.zoom_factor)

    def zoomOut(self):
        self.zoom_factor-=.1
        self.page.setZoomFactor(self.zoom_factor)

    def show_next_dict(self):
        name=MainWindow.dictionaries[MainWindow.dict_index][0]
        if name not in self.result_obj:
            MainWindow.dict_index = (MainWindow.dict_index + 1) % len(MainWindow.dictionaries)
            self.show_next_dict()
            return

        data_folder=MainWindow.dictionaries[MainWindow.dict_index][2]
        html=pretty_dict_result(name,self.result_obj[name])
        print(data_folder)
        self.page.setHtml(html, QUrl.fromLocalFile(data_folder+"/"))
        MainWindow.dict_index = (MainWindow.dict_index + 1) % len(MainWindow.dictionaries)

    def lookup(self,word=None):
        if not word:
            word=self.line_edit.text().strip()
        self.result_obj=SocketClient.lookup(word)
        #baseUrl = QUrl.fromLocalFile("/index.html")
        #print(baseUrl)
        #html=join_dict_results(result_obj)
        MainWindow.dict_index=0
        MainWindow.history=[word]
        self.show_next_dict()

    def showMessage(self,msg):
        self.status_bar.showMessage(str(msg),4000)



