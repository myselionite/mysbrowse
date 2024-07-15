import os
import sys
import pickle
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *

class TabSystem(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_current_tab)
        self.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.setMovable(True)
        self.add_new_tab(QUrl("http://www.google.com"), "Homepage")

    def add_new_tab(self, qurl="", label="Blank", session_state=None):
        if qurl is None:
            qurl = QUrl('https://www.google.com/')

        browser = QWebEngineView()
        if session_state:
            browser.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            browser.page().profile().setPersistentStoragePath(session_state['persistent_storage_path'])
            for cookie in session_state['cookies']:
                browser.page().profile().cookieStore().setCookie(cookie)
        else:
            browser.setUrl(QUrl("https://www.google.com"))
        i = self.addTab(browser, label)
        self.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.set_tab_title(i, browser))

    def set_tab_title(self, i, browser):
        title = browser.page().title()
        self.setTabText(i, title)

    def update_urlbar(self, qurl, browser=None):
        if browser != self.currentWidget():
            return
        self.parent().url_bar.setText(qurl.toString())

    def close_current_tab(self, i):
        if self.count() < 2:
            return
        self.removeTab(i)

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

class MysBrowse(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QMainWindow {
                background-color: #7E57C2;
            }
            QToolBar {
                background-color: #5E35B1;
                border: none;
            }
            QLineEdit {
                background-color: #9575CD;
                color: white;
                padding: 5px;
                border-radius: 10px;
                border: 2px solid #5E35B1;
            }
            QPushButton, QAction {
                background-color: #673AB7;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover, QAction:hover {
                background-color: #5E35B1;
            }
        """)

        self.tabs = TabSystem()
        self.setCentralWidget(self.tabs)
        self.showMaximized()
        self.setWindowTitle("MysBrowse")

        nav_bar = QToolBar()
        self.addToolBar(nav_bar)
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.tabs.currentWidget().back)
        nav_bar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.tabs.currentWidget().forward)
        nav_bar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.tabs.currentWidget().reload)
        nav_bar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.navigate_home)
        nav_bar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        # Connect the editingFinished signal of the URL bar to the clear_url_bar method
        self.url_bar.editingFinished.connect(self.clear_url_bar)
        # Connect the mousePressEvent event of the URL bar to the clear_url_bar method
        self.url_bar.mousePressEvent = lambda event: self.clear_url_bar()
        nav_bar.addWidget(self.url_bar)

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.clicked.connect(lambda: self.tabs.add_new_tab())
        nav_bar.addWidget(self.new_tab_btn)
        self.tabs.currentChanged.connect(self.update_url)
        self.tabs.currentWidget().urlChanged.connect(self.update_url)


    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.tabs.currentWidget().setUrl(QUrl(url))
        input_text = self.url_bar.text()
        if input_text:
            url = QUrl(input_text)
            
            # Check if the input text is a valid URL
            if url.isValid() and url.scheme() in ['http', 'https', 'ftp']:
                # If it's a valid URL with http, https, or ftp scheme
                self.tabs.currentWidget().setUrl(url)
            elif not url.scheme() and ('.' in input_text):
                # If there's a dot but no scheme, prepend 'https://'
                # Check if it contains a space and a dot
                if ' ' not in input_text or ('.' in input_text and ' ' in input_text):
                    # If it contains a dot and not just a search term with spaces
                    url = QUrl(f"https://google.com/search?q={input_text}")
                    self.tabs.currentWidget().setUrl(url)
                else:
                    # If it contains spaces but not a dot, treat it as a search query
                    search_query = '+'.join(input_text.split())
                    search_url = QUrl(f"https://www.google.com/search?q={search_query}")
                    self.tabs.currentWidget().setUrl(search_url)
            else:
                # For cases where input might be just a query without a dot or scheme
                if ' ' in input_text:
                    search_query = '+'.join(input_text.split())
                    search_url = QUrl(f"https://www.google.com/search?q={search_query}")
                    self.tabs.currentWidget().setUrl(search_url)
                else:
                    # If none of the above, treat it as a search query
                    search_query = '+'.join(input_text.split())
                    search_url = QUrl(f"https://www.google.com/search?q={search_query}")
                    self.tabs.currentWidget().setUrl(search_url)
        else:
            # If no input is provided, navigate to the default search engine
            search_query = '+'.join("MysBrowse")
            search_url = QUrl(f"https://www.google.com/search?q={search_query}")
            self.tabs.currentWidget().setUrl(search_url)
    def clear_url_bar(self):
        # Clear the contents of the URL bar on click
        self.url_bar.clear()

    def update_url(self):
        qurl = self.tabs.currentWidget().url()
        self.url_bar.setText(qurl.toString())

    def save_credentials(self):
        # Note: This does not serve to transfer any passwords, they are (if they are even being detected) stored in your C:\Program Files folder, under the name "credentials.txt".
        passwords_dir = "C:\\Program Files\\MysBrowse_Passwords"
        if not os.path.exists(passwords_dir):
            os.makedirs(passwords_dir)

        with open(os.path.join(passwords_dir, "credentials.txt"), "w") as file:
            for tab_index in range(self.tabs.count()):
                browser = self.tabs.widget(tab_index)
                email = browser.page().runJavaScript("document.getElementById('identifierId').value")
                password = browser.page().runJavaScript("document.getElementById('password').value")
                if email and password:
                    file.write(f"Email: {email}\nPassword: {password}\n\n")

    def closeEvent(self, event):
        self.save_session_state()
        event.accept()

    def save_session_state(self):
        session_state = {'tabs': []}
        for tab_index in range(self.tabs.count()):
            browser = self.tabs.widget(tab_index)
            cookies = browser.page().profile().cookieStore().getAllCookies()
            persistent_storage_path = browser.page().profile().persistentStoragePath()
            session_state['tabs'].append({'cookies': cookies, 'persistent_storage_path': persistent_storage_path})
        with open("session_state.pkl", "wb") as file:
            pickle.dump(session_state, file)

    def restore_session_state(self):
        if os.path.exists("session_state.pkl"):
            with open("session_state.pkl", "rb") as file:
                session_state = pickle.load(file)
                for tab_state in session_state['tabs']:
                    self.tabs.add_new_tab(session_state=tab_state)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("MysBrowse")
    window = MysBrowse()
    window.restore_session_state()
    app.exec_()
