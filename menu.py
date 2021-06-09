from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMainWindow
from widgets import PushButton
from Styles.styles import (MAIN_BG, TEXT_STYLE, BTN_STYLE)
from main import *

class MainWindow(QMainWindow):

    #Signal to send values between pages
    goto_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        #Setting up ui components.
        self.w, self.h = 529, 523
        self.w_factor, self.h_factor = 1, 1
        self.setMinimumSize(self.w, self.h)
        self.setStyleSheet(MAIN_BG)

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setLayout(QVBoxLayout())
        self.setCentralWidget(self.central_widget)
        self.label_container = QWidget()
        self.btn_container = QWidget()
        self.label_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()

        self.label_layout.setAlignment(Qt.AlignCenter)
        self.label_container.setLayout(self.label_layout)
        self.btn_container.setLayout(self.btn_layout)

        self.setup_label()
        self.setup_button()
        self.central_widget.layout().addWidget(self.label_container)
        self.central_widget.layout().addWidget(self.btn_container)

    def goto(self, name):
        #Emit goto_signal to a connected method, sending the name of a page and switch the page
        self.goto_signal.emit(name)

    def setup_label(self):
        self.title = QLabel("POMODORO TIMER", self)
        self.info_text = QLabel("Choose Options Below to Get Started !", self)

        self.title.setFont(QFont("Arial", 29, 75))
        self.title.setStyleSheet(TEXT_STYLE)
        self.info_text.setFont(QFont("Bahnschrift Light", 16))
        self.info_text.setStyleSheet(TEXT_STYLE)
        self.center_spacer = QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.bottom_spacer = QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.top_spacer = QSpacerItem(0, 70, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.label_layout.addItem(self.top_spacer)
        self.label_layout.addWidget(self.title)
        self.label_layout.addItem(self.center_spacer)
        self.label_layout.addWidget(self.info_text)
        self.label_layout.addItem(self.bottom_spacer)

    def setup_button(self):
        #Setting up buttons and sending a page name when clicked to the button_handler method
        
        tab = '\t'*6
        self.btn_work = PushButton(f"{tab}Work{tab}", self, clicked=lambda: self.button_handler("Work"))
        self.btn_short = PushButton("\tShort Break\t", self, clicked=lambda: self.button_handler("Short"))
        self.btn_long = PushButton("\tLong Break\t", self, clicked=lambda: self.button_handler("Long"))
        side_spacer = QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        btn_spacer = QSpacerItem(20,10, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.btn_container.layout().addItem(side_spacer)

        for i in ('work', 'short', 'long'):
            eval(f"self.btn_{i}.setFont(QFont('Bahnschrift Light', 14))")
            eval(f"self.btn_{i}.setStyleSheet(BTN_STYLE)")
            eval(f"self.btn_container.layout().addWidget(self.btn_{i})")
            if i != 'long':
                self.btn_container.layout().addItem(btn_spacer)
                
        self.btn_container.layout().addItem(side_spacer)

    def button_handler(self, command):
        #Changing the page
        self.goto(command)

    def resizeEvent(self, event):
        self.w_factor = self.rect().width() / self.w
        self.h_factor = self.rect().height() / self.h 

        self.title.setFont(QFont("Arial", 29*self.h_factor, 75))
        self.info_text.setFont(QFont("Bahnschrift Light", 16*self.h_factor))
        self.center_spacer.changeSize(0, 110*self.h_factor)
        self.bottom_spacer.changeSize(0, 53*self.h_factor)
        self.top_spacer.changeSize(0, 70*self.h_factor)

        for i in ('work', 'short' ,'long'):
            eval(f"self.btn_{i}.setMaximumHeight(51*self.h_factor)")
            eval(f"self.btn_{i}.setFont(QFont('Bahnschrift Light', 14*self.h_factor))")
            eval(f"self.btn_{i}.setStyleSheet(BTN_STYLE.format(4*self.h_factor, 5*self.h_factor))")