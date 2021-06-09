from PyQt5.QtCore import QEvent, Qt, pyqtSignal, QRect, QPoint
from PyQt5.QtWidgets import QLineEdit, QDialog, QPushButton, QWidget, QTabBar, QLabel, QStylePainter, QStyleOptionTab, QStyle, QAbstractSpinBox, QMainWindow, QSpinBox, QComboBox
from PyQt5.QtGui import QCursor, QFont, QIcon
from Styles.styles import MAIN_BG
from json import load, dump
from os import makedirs, path

class LineEdit(QLineEdit):
    unfocus_value = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def focusOutEvent(self, event):
        self.unfocus_value.emit(self.text())

class Dialog(QDialog):
    name_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgb(203, 73, 75)")

    def closeEvent(self, event):
        if not event:
            self.name_signal.emit("")

class PushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))

class CustomCheckButton(PushButton):

    def __init__(self, parent=None, is_checked=False):
        super().__init__(parent)
        self.parent = parent
        self.is_checked = is_checked
        if self.is_checked:
            self.setIcon(QIcon("Assets/IMG/checked.png"))
        else:
            self.setIcon(QIcon("Assets/IMG/unchecked.png"))
        self.clicked.connect(self.check_event)

    def check_event(self):
        if self.is_checked:
            self.is_checked = False
            self.setIcon(QIcon("Assets/IMG/unchecked.png"))
        else:
            self.is_checked = True
            self.setIcon(QIcon("Assets/IMG/checked.png"))

class InputBox(QMainWindow):

    def __init__(self, input_type, parent):
        super().__init__(parent)
        self.input_type = input_type
        self.init_ui()

    def init_ui(self):
        if self.input_type == 'SpinBox':
            self.widget = QSpinBox(self)
        else:
            self.widget = QComboBox(self)
        
        self.widget.installEventFilter(self)
        self.setCentralWidget(self.widget)

    def eventFilter(self, widget, event):
        if (event.type() == QEvent.Enter):
            if self.input_type == 'SpinBox':
                widget.setButtonSymbols(QAbstractSpinBox.PlusMinus)

        elif (event.type() == QEvent.Leave):
            if self.input_type == 'SpinBox':
                widget.setButtonSymbols(QAbstractSpinBox.NoButtons)

        return super().eventFilter(widget, event)

class TabBar(QTabBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TabBar")

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt);
            painter.restore()

def restore(widget):
    PATH = "Settings/settings.json"
    try:
        with open(PATH) as f:
            data = load(f)
    except:
        makedirs(path.dirname(PATH), exist_ok=True)
        with open(PATH, 'w+') as f:
            data = {"Pomodoro":{'work_time':25,'short_time':5,'long_time':15,'auto_start':False,'break_interval':3},"Todolist":{}}
            dump(data, f, indent=3)

    return data[widget]

def dump_file(widget, saved_settings={}):
    PATH = "Settings/settings.json"
    with open(PATH) as f:
        data = load(f)
        data[widget] = saved_settings
        with open(PATH, 'w') as f:
            dump(data, f, indent=3)

def save(widget, properties=None):
    if widget.objectName() == 'Todolist':
        saved_settings = {"Tabs":len(properties), "Current Index":widget.currentIndex()}

        for index, subtask in enumerate(properties):
            current_subtask = f"Subtask {index+1}"
            saved_settings[current_subtask] = {"Title":None, "Checkboxes":[{"Name":None, "Is_Checked":False} for _ in range(len(subtask.checkboxes))]}
            saved_settings[current_subtask]["Title"] = subtask.title
            for c_index, value in enumerate(subtask.checkboxes.values()):
                saved_settings[current_subtask]["Checkboxes"][c_index]["Name"] = value.name
                saved_settings[current_subtask]["Checkboxes"][c_index]["Is_Checked"] = value.task.is_checked
    else:
        saved_settings = {}
        for var in ('work_time', 'short_time', 'long_time', 'auto_start', 'break_interval'):
            if var == 'auto_start':
                auto_start = True if widget.auto_start[1].widget.currentText() == 'True' else False
            else:
                exec(f"{var} = int(widget.{var}[1].widget.text())")
            saved_settings[var] = eval(var)

    dump_file(widget.objectName(), saved_settings)