import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *


# Prepare for the most unreadable code ever!
class TabSystem(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_current_tab)
        self.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.setMovable(True)

        # Start with the almighty Google as the default tab
        self.add_new_tab(QUrl("http://www.google.com"), "Homepage")

    def add_new_tab(self, qurl="", label="Blank"):
        if qurl is None:
            qurl = QUrl('')

        browser = QWebEngineView()
        browser.setUrl(QUrl("https://www.google.com"))
        i = self.addTab(browser, label)  # Add the new tab to the end
        self.setCurrentIndex(i)

        # Update the URL bar and tab title when necessary
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.set_tab_title(i, browser))

    def set_tab_title(self, i, browser):
        title = browser.page().title()
        self.setTabText(i, title)

    def update_urlbar(self, qurl, browser=None):
        if browser != self.currentWidget():
            # If this isn't the active tab, who cares
            return

        self.parent().url_bar.setText(qurl.toString())

    def close_current_tab(self, i):
        if self.count() < 2:
            # Don't be a hero, we need at least one tab open
            return

        self.removeTab(i)

    def tab_open_doubleclick(self, i):
        if i == -1:
            # Give me the fucking tabs
            self.add_new_tab()

class MysBrowse(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the stylesheet because we want to look good

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


        # YandereDEV type shit right here
        self.tabs = TabSystem()
        self.setCentralWidget(self.tabs)
        self.showMaximized()
        self.setWindowTitle("MysBrowse")

        # Create the navigation bar because we need some control
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        # Back button: Go back in time (sort of)
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.tabs.currentWidget().back)
        nav_bar.addAction(back_btn)

        # Forward button: Because sometimes you regret going back
        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.tabs.currentWidget().forward)
        nav_bar.addAction(forward_btn)

        # Reload button: Click it when you panic
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.tabs.currentWidget().reload)
        nav_bar.addAction(reload_btn)

        # Home button: Because there's no place like home
        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.navigate_home)
        nav_bar.addAction(home_btn)

        # URL bar: Type your heart out
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        # New tab button: The more, the merrier, not for your computer, though
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.clicked.connect(lambda: self.tabs.add_new_tab())
        nav_bar.addWidget(self.new_tab_btn)

        # Update the URL bar when switching tabs
        self.tabs.currentChanged.connect(self.update_url)
        self.tabs.currentWidget().urlChanged.connect(self.update_url)

    def navigate_home(self):
        # Bring me home, Scotty!
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self):
        qurl = self.tabs.currentWidget().url()
        self.url_bar.setText(qurl.toString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("MysBrowse")
    window = MysBrowse()
    app.exec_()
