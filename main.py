from timer import *
from PyQt5.QtCore import QRect, pyqtSlot
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QApplication, QDesktopWidget, QAction

class Window(QMainWindow):
    """Window(QMainWindow) -> A class to create switchable pages. Credit to eyllanesc."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pomodoro Timer")
        self.setWindowIcon(QIcon("Assets/IMG/icon.png"))
        self.setGeometry(QRect(300, 300, 529, 523))
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.center_the_screen()

        self.m_pages = {}
        self.fullscreen = QAction("&Fullscreen", self)

        self.fullscreen.setShortcut("F11")
        self.fullscreen.triggered.connect(self.toggle_fullscreen)
        self.fullscreen.setStatusTip("Change to fullscreen mode")
        self.addAction(self.fullscreen)

        for name in ('Main', 'Work', 'Short', 'Long'):
            if name != 'Main':
                self.register(Timer(name, self), name)
            else:
                self.register(MainWindow(), name)
            self.m_pages[name].init_ui()

        self.m_pages["Todolist"] = Todolist(True)
        self.m_pages["Settings"] = Settings(self)

        self.goto("Main")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def center_the_screen(self):
        current_size = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        current_size.moveCenter(center_point)
        self.move(current_size.topLeft())

    def register(self, widget, name):
        #Register all those pages to the stacked widget
        self.m_pages[name] = widget
        self.stacked_widget.addWidget(widget)
        if isinstance(widget, MainWindow):
            widget.goto_signal.connect(self.goto)

    @pyqtSlot(str)
    def goto(self, name):
        #A func to Switch between pages
        if name in self.m_pages:
            widget = self.m_pages[name]
            self.stacked_widget.setCurrentWidget(widget)
            #print(self.stacked_widget.currentIndex())


if __name__ == '__main__':
    app = QApplication([])
    win = Window()
    win.show()
    app.exec_()