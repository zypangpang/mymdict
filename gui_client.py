from PyQt5.QtCore import QUrl, QDir
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEnginePage
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWebEngineWidgets
from PyQt5 import QtCore

from dict_parse.mymdict import MDX

print("Loading dictionaries from file ...")
mdx = MDX("/mnt/document/Dictionary/L6mp3.mdx")
word_map={}
for index,key_tuple in enumerate(mdx._key_list):
    word_map[key_tuple[1].decode("utf-8")]=index
print("Done")

def lookup(word):
    #mdx=MDX("LongmanDict.mdx")
    index=word_map[word]
    word,record = mdx._decode_record_by_key_start(index)
    return word.decode("UTF-8"), record.decode("UTF-8")
    #return mdx.items().__next__()[0]
    #for key,value in mdx.items():
    #    key=key.decode('UTF-8')
    #    if key == word:
    #        return value
def search():
    print("********** Search *****************")
    while True:
        word = input("word:")
        w, r = test(word)
        print(w)
        print(r)
def output(word):
    _,record=test(word)
    print(record)

def loadJS(view,SCRIPT,name):
    script = QtWebEngineWidgets.QWebEngineScript()
    view.page().runJavaScript(SCRIPT, QtWebEngineWidgets.QWebEngineScript.ApplicationWorld)
    script.setName(name)
    script.setSourceCode(SCRIPT)
    script.setInjectionPoint(QtWebEngineWidgets.QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    script.setWorldId(QtWebEngineWidgets.QWebEngineScript.MainWorld)
    view.page().scripts().insert(script)

def load_css_js_from_file(type,view,path,name):
    path = QtCore.QFile(path)
    if not path.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        return
    content = path.readAll().data().decode("utf-8")
    if type=='css':
        loadCSS(view,content,name)
    else:
        loadJS(view,content,name)

def loadCSS(view, css, name):
    SCRIPT = """
    (function() {
    css = document.createElement('style');
    css.type = 'text/css';
    css.id = "%s";
    document.head.appendChild(css);
    css.innerText = `%s`;
    })()
    """ % (name, css)

    loadJS(view,SCRIPT,name)


def set_default_font():
    fontDataBase = QFontDatabase()
    defaultSettings = QWebEngineSettings.globalSettings()
    standardFont = fontDataBase.font("Noto Sans CJK SC", "", 12)
    defaultSettings.setFontFamily(QWebEngineSettings.StandardFont, standardFont.family())
    defaultSettings.setFontSize(QWebEngineSettings.DefaultFontSize, 18)

class MyWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url: QUrl, type: QWebEnginePage.NavigationType, isMainFrame: bool, **kwargs):
        print(type)
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            print(url)
            scheme,item = url.toString().split("://")
            _,record=lookup(item)
            print(self.url())
            self.setHtml(record,self.url())
            return False
        return True




def test_qt():
    #header='<meta charset="UTF-8"/>\n'
    _,record=lookup("mouse")
    #print(QDir.currentPath())
    #print(record)
    #record=header+record
    app=QApplication([])
    set_default_font()
    view = QtWebEngineWidgets.QWebEngineView()
    page=MyWebPage()
    view.setPage(page)
    baseUrl = QUrl.fromLocalFile(QDir.currentPath() + "/index.html")
    print(baseUrl)
    page.setHtml(record,baseUrl)
    #view.load(QUrl("file://t.html"))
    #load_css_js_from_file('css',view,"LDOCE6.css","ld6")
    #load_css_js_from_file('js',view,"entry.js","entry")
    view.show()
    app.exec_()

if __name__ == '__main__':
    #output(300)
    test_qt()


