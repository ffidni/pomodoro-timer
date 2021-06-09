from widgets import LineEdit, CustomCheckButton, Dialog, TabBar, PushButton, save, restore
from PyQt5.QtWidgets import QSizePolicy, QLabel, QTabWidget, QScrollArea, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QCursor, QFontMetrics
from Styles.styles import TODOLIST_STYLE

def set_task_name(widget, index, closable=False):
    widget.dialog = Dialog()
    widget.dialog.setWindowIcon(QIcon("Assets/IMG/task.png"))
    widget.layout = QHBoxLayout()
    widget.name = LineEdit(widget.dialog)
    widget.enter = PushButton("Create", widget.dialog)

    widget.dialog.setWindowFlags(widget.dialog.windowFlags() & Qt.CustomizeWindowHint)
    widget.dialog.setWindowFlags(widget.dialog.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
    if not closable: 
        widget.dialog.setWindowFlags(widget.dialog.windowFlags() & ~Qt.WindowCloseButtonHint)

    widget.name.setFixedSize(150, 20)
    widget.name.setStyleSheet("background-color: rgb(248, 237, 227);")

    widget.enter.setFixedSize(50, 20)
    widget.enter.setStyleSheet("background-color: rgb(248, 237, 227)")

    widget.dialog.name_signal.connect(widget.name.setText)

    widget.dialog.setWindowTitle("Add a task name")
    widget.dialog.setFixedSize(250, 50)

    def send_click():
        widget.dialog.enter_clicked = True
        dialog_handler(widget=widget, index=index, closable=closable)

    widget.enter.clicked.connect(send_click)
    widget.layout.addWidget(widget.name)
    widget.layout.addWidget(widget.enter)
    widget.dialog.setLayout(widget.layout)
    widget.dialog.exec_()

    return widget.name.text()

def dialog_handler(widget, index, closable):
    widget.dialog.close()
    if not widget.name.text():
        QApplication.beep()
        set_task_name(widget, index, closable)

class Todolist(QTabWidget):

    def __init__(self, first=False, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.first = first
        self.w, self.h = 380, 400
        self.w_factor, self.h_factor = 1, 1
        self.is_deleted = False
        self.setWindowTitle("To Do List")
        self.setObjectName("Todolist")
        self.setTabBar(TabBar(self))
        self.setTabPosition(QTabWidget.West)
        self.resize(self.w, self.h)
        self.setStyleSheet(TODOLIST_STYLE)
        self.setWindowIcon(QIcon("Assets/IMG/task.png"))

        self.settings = restore('Todolist')
        self.init_ui()
    
    def init_ui(self):
        #Setting up ui components
        self.tabBar().installEventFilter(self)
        self.tabBar().setMouseTracking(True)
        self.subtasks = []

        #Restoring settings value
        if self.settings:
            for tab in range(self.settings["Tabs"]):
                title = self.settings[f"Subtask {tab+1}"]["Title"]
                checkboxes = self.settings[f"Subtask {tab+1}"]["Checkboxes"]
                current_index = self.settings["Current Index"]
                widget = Subtask(title=title, parent=self, index=tab+1, checkbox_props=checkboxes)
                self.addTab(widget, QIcon(""), title)
                self.subtasks.append(widget)
                self.setCurrentIndex(current_index)


        self.addTab(QWidget(), QIcon(""), "    New    ")
        QTimer.singleShot(100, self.new_task)
        self.currentChanged.connect(lambda i : self.new_task(self.is_deleted, i))
        self.font = QFont("Arial", 10)
        self.setFont(self.font)

    def delete_task(self):
        current_index = self.currentIndex()
        self.widget(current_index).deleteLater()
        self.setCurrentIndex(current_index-1)
        self.is_deleted = False
        del self.subtasks[current_index]

    def change_title(self, title, index=None):
        length = len(title)-1
        if length >= 25:
            title = title[:length-(length-25)] + "..."

        self.setTabText(index+1 if index != None else self.currentIndex(), title)
        return title

    def new_task(self, is_deleted=False, index=0):
        if not self.first:
            if index == self.count()-1 and not is_deleted:
                title = set_task_name(self, index)
                if title:
                    exec(f"self.task_{index+1} = Subtask(title=title, index={index+1}, parent=self)")
                    self.subtasks.append(eval(f"self.task_{index+1}"))
                    self.insertTab(index, eval(f"self.task_{index+1}"), QIcon(""), self.change_title(title, index))
                    self.setCurrentIndex(index)
                elif not title and index == 0:
                    self.new_task(self.is_deleted, self.count()-1)
                else:
                    self.setCurrentIndex(index-1)

    def eventFilter(self, widget, event):
        #Changing the cursor when hovering on a certain tab
        if (event.type() == QEvent.MouseMove and widget == self.tabBar()):
            index = widget.tabAt(event.pos())
            if index >= 0 and index != widget.currentIndex():
                widget.setCursor(Qt.PointingHandCursor)
            else:
                widget.setCursor(Qt.ArrowCursor)
            
        return super().eventFilter(widget, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.w_factor = self.rect().width() / self.w
        self.h_factor = self.rect().height() / self.h
        self.font.setPointSize(10*self.h_factor)
        self.setFont(self.font)

class Subtask(QScrollArea):
    sizes_signal = pyqtSignal(tuple)

    def __init__(self, title="", parent=None, index=None, checkbox_props=None):
        super().__init__(parent)
        self.title = title
        self.index = index
        self.parent = parent
        self.w, self.h = 380, 400
        self.w_factor, self.h_factor = 1, 1
        self.checkbox_props = checkbox_props
        self.setStyleSheet("""QWidget{background-color: transparent;}
                            QScrollArea {
                                background: transparent;
                                border: none;}
                              QScrollArea > QWidget > QWidget { background: transparent; }
                              QScrollArea > QWidget > QScrollBar { background: pallete(window); }""")
        self.init_ui()

    def init_ui(self):
        self.widget = QWidget()
        self.mlayout = QVBoxLayout(self)
        self.hlayout = QHBoxLayout(self)
        self.vlayout = QVBoxLayout(self)
        self.vlayout_2 = QVBoxLayout(self)

        self.widget.setObjectName(f"Widget {self.index}")

        self.checkboxes = {}

        self.show_title(self.title)
        if self.checkbox_props:
            self.create_checkbox(restore=True)
        self.new_btn = PushButton("", self, clicked= lambda: self.btn_handler("New"))

        self.new_btn.setObjectName(f"Plus Button {self.index}")
        self.new_btn.setFont(QFont("Bahnschrift Light", 24))
        self.new_btn.setIcon(QIcon("Assets/IMG/plus.png"))

        self.mlayout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.hlayout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.vlayout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.vlayout_2.setAlignment(Qt.AlignHCenter | Qt.AlignCenter)

        self.vlayout_2.addWidget(self.new_btn)
        self.mlayout.addLayout(self.hlayout)
        self.mlayout.addLayout(self.vlayout)
        self.mlayout.addLayout(self.vlayout_2)
        self.widget.setLayout(self.mlayout)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)

    def create_checkbox(self, restore=False):
        def checkbox_settings(widget, count):
            widget.task_name.setFont(QFont("Arial", 10*self.h_factor))
            #widget.task_delete_signal.connect(lambda signal: self.delete_task(signal, count, widget))
            widget.installEventFilter(self)
            self.vlayout.addWidget(current_checkbox)
        
        if restore:
            for index in range(len(self.checkbox_props)):
                name = self.checkbox_props[index]["Name"]
                is_checked = self.checkbox_props[index]["Is_Checked"]
                exec(f'self.checkbox_{index+1} = Checkbox("{name}", {index+1}, {self.index}, is_checked, self)')
                current_checkbox = eval(f"self.checkbox_{index+1}")
                self.checkboxes[index+1] = current_checkbox
                checkbox_settings(current_checkbox, index+1)
                
        else:
            name = set_task_name(self, self.index, True)
            if name:
                count = len(self.checkboxes)+1 if self.checkboxes else 1
                exec(f'self.checkbox_{count} = Checkbox("{name}", {count}, {self.index}, False, self)')
                current_checkbox = eval(f"self.checkbox_{count}")
                self.checkboxes[count] = current_checkbox
                checkbox_settings(current_checkbox, count)

        self.sizes_signal.emit((self.w, self.h, self.w_factor, self.h_factor))
            
    def show_title(self, text):
        self.label = QLabel(text, self)
        self.label.setObjectName(f"Title {self.index}")
        self.label.setText(text)
        self.label.setFont(QFont("Arial", 16*self.h_factor))
        self.label.setCursor(QCursor(Qt.IBeamCursor))
        self.label.setStyleSheet("color: white;")
        self.label.installEventFilter(self)
        self.hlayout.addWidget(self.label)
        self.show_settings()

    def show_settings(self):
        try:
            self.hlayout.removeWidget(self.settings_btn)
            self.settings_btn.deleteLater()
        except:
            pass

        self.settings_btn = PushButton("", self, clicked= lambda: self.btn_handler("Settings"))

        self.settings_btn.setObjectName(f"Settings Button {self.index}")
        self.settings_btn.setStyleSheet("""border: none;""")
        self.settings_btn.setIcon(QIcon("Assets/IMG/settings.png"))
        self.settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.settings_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.settings_btn.setFixedSize(20, 20)
        self.hlayout.addWidget(self.settings_btn)

        try:
            self.label_input.setFocus()
        except:
            pass


    def change_label(self, idle_text=None):
        if idle_text:
            new_text = idle_text
        else:
            new_text = self.label_input.text()

        if new_text:
            self.parent.setTabText(self.index-1, new_text)

        try:
            self.label_input.deleteLater()
        except:
            pass

        self.show_title(new_text)

    def show_input(self):
        old_text = self.label.text()
        self.label_input = LineEdit(self)

        self.hlayout.removeWidget(self.label)
        self.label.deleteLater()
        self.label_input.setObjectName(f"Label Input {self.index}")
        self.label_input.unfocus_value.connect(lambda signal: QTimer.singleShot(10, self.change_label))
        self.label_input.setText(old_text)
        self.label_input.setStyleSheet("""
                         QLineEdit{
                            color: white;
                            border: none;
                         }
                            """)
        self.fit_content(self.label_input)
        self.label_input.setAlignment(Qt.AlignCenter)
        self.label_input.textChanged.connect(lambda: self.fit_content(self.label_input))
        self.label_input.setFont(QFont("Arial", 16*self.h_factor))
        self.label_input.returnPressed.connect(self.change_label)

        self.hlayout.addWidget(self.label_input)
        self.show_settings()
            
    def fit_content(self, widget):
        text = widget.text()
        font = QFont("Arial", 0)
        fm = QFontMetrics(font)
        width = fm.width(text)
        height = fm.height()
        main_width = self.width()
        widget.setFixedSize(width+20, height)

    def settings(self):
        self.settings_dialog = Dialog()
        self.layout = QHBoxLayout()
        self.change_btn = PushButton("Change name", self.settings_dialog, clicked= lambda: self.btn_handler("Change"))
        self.delete_btn = PushButton("Delete this task", self.settings_dialog, clicked= lambda: self.btn_handler("Delete"))

        self.settings_dialog.setObjectName(f"Settings Dialog {self.index}")
        self.settings_dialog.setWindowTitle("Task Settings")
        self.settings_dialog.setFixedSize(250, 65)
        self.change_btn.setObjectName(f"Change Button {self.index}")
        self.change_btn.setFixedSize(85, 30)
        self.change_btn.setStyleSheet("background-color: rgb(248, 237, 227);")
        self.delete_btn.setObjectName(f"Delete Button {self.index}")
        self.delete_btn.setFixedSize(85, 30)
        self.delete_btn.setStyleSheet("background-color: rgb(248, 237, 227);")
        self.layout.addWidget(self.change_btn)
        self.layout.addWidget(self.delete_btn)
        self.settings_dialog.setLayout(self.layout)

        self.settings_dialog.exec_()

    def delete_task(self, index, widget):
        try:
            self.vlayout.removeWidget(widget)
        except:
            pass

        try:
            widget.deleteLater()
        except:
            pass

        self.checkboxes.pop(index)

    def btn_handler(self, command, is_dialog=False, closable=False):
        if command == 'New':
            self.create_checkbox()
        elif command == 'Settings':
            self.settings()
        elif command == 'Change':
            self.settings_dialog.close()
            QTimer.singleShot(100, self.show_input)
        elif command == 'Delete':
            self.settings_dialog.close()
            self.parent.delete_task()

    def eventFilter(self, widget, event):
        if event.type() == QEvent.MouseButtonPress:
            if widget in self.checkboxes.values():
                try:
                    widget.show_input()
                except:
                    pass
            elif widget == self.label:
                try:
                    self.show_input()
                except:
                    pass
                    
        return super().eventFilter(widget, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.w_factor = self.rect().width() / self.w
        self.h_factor = self.rect().height() / self.h

        self.sizes_signal.emit((self.w, self.h, self.w_factor, self.h_factor))

        try:
            self.label.setFont(QFont("Arial", 16*self.h_factor))
        except:
            self.label_input.setFont(QFont("Arial", 16*self.h_factor))
            self.fit_content(self.label_input)

        self.new_btn.setFont(QFont("Bahnschrift Light", 24*self.h_factor))
        self.new_btn.setFixedSize(self.w*0.25*self.w_factor, self.h*0.1*self.h_factor)
        self.new_btn.setIconSize(QSize(self.w*0.25*self.w_factor, self.h*0.1*self.h_factor))

class Checkbox(QWidget):

    def __init__(self, name, count, index, is_checked=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.index = index
        self.count = count
        self.is_checked = is_checked
        self.parent = parent
        self.w, self.h = 1, 1
        self.w_factor, self.h_factor = 1, 1
        self.setObjectName(f"Checkbox {self.index}x{self.count}")
        self.parent.sizes_signal.connect(self.change_size)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

        self.init_ui()


    def init_ui(self):
        self.mlayout = QHBoxLayout()
        self.hlayout = QHBoxLayout()
        self.hlayout_2 = QHBoxLayout()
        self.task = CustomCheckButton(self, self.is_checked)
        self.task.setObjectName(f"Check Button {self.index}x{self.count}")

        self.hlayout.addWidget(self.task)
        self.task.clicked.connect(self.btn_handler)

        self.show_task()
        self.show_tools()

        self.mlayout.addLayout(self.hlayout)
        self.mlayout.addLayout(self.hlayout_2)
        self.setLayout(self.mlayout)

    def change_size(self, new):
        self.w, self.h = new[0], new[1]
        self.w_factor, self.h_factor = new[2], new[3]
        try:
            self.task.setFixedSize(self.w*0.05*self.w_factor, self.h*0.1*self.h_factor)
            self.task.setIconSize(QSize(self.w*0.05*self.w_factor, self.h*0.1*self.h_factor))

            try:
                self.task_name.setFont(QFont("Arial", 10*self.h_factor))
                self.task_name.setMinimumSize(self.w*0.25*self.w_factor, self.h*0.1*self.h_factor)
            except:
                self.task_input.setFont(QFont("Arial", 10*self.h_factor))
                self.task_input.setMinimumSize(self.w*0.25*self.w_factor, self.h*0.1*self.h_factor)

            self.rename.setFixedSize(self.w*0.05*self.w_factor, self.h*0.09*self.h_factor)
            self.rename.setIconSize(QSize(self.w*0.05*self.w_factor, self.h*0.09*self.h_factor))
            self.delete.setFixedSize(self.w*0.05*self.w_factor, self.h*0.09*self.h_factor)
            self.delete.setIconSize(QSize(self.w*0.05*self.w_factor, self.h*0.09*self.h_factor))
        except:
            pass

    def show_input(self):
        self.old_text = self.task_name.text()
        self.task_input = LineEdit(self)

        self.hlayout.removeWidget(self.task_name)
        self.task_name.deleteLater()

        self.task_input.unfocus_value.connect(self.show_task)
        self.task_input.setStyleSheet("""color: white;
                                        border: none;""")
        self.task_input.setText(self.old_text)
        self.task_input.setFocus()
        self.task_input.setMinimumSize(self.w*0.25*self.w_factor, self.h*0.1*self.h_factor)
        self.task_input.setFont(QFont("Arial", 10*self.h_factor))
        self.task_input.returnPressed.connect(self.show_task)
        self.hlayout.addWidget(self.task_input)
        
    def show_tools(self):
        self.task.setFixedSize(15, 30)

        self.rename = PushButton(self, clicked= lambda: self.btn_handler("Rename"))
        self.delete = PushButton(self, clicked= lambda: self.btn_handler("Delete"))
        self.rename.setObjectName(f"Rename Button {self.index}")
        self.rename.setIcon(QIcon("Assets/IMG/pen.png"))
        self.rename.setFixedSize(16, 16)
        self.rename.setCursor(QCursor(Qt.PointingHandCursor))
        self.rename.setObjectName(f"Delete Button {self.index}")
        self.delete.setFixedSize(16, 16)
        self.delete.setIcon(QIcon("Assets/IMG/trashcan.png"))
        self.delete.setCursor(QCursor(Qt.PointingHandCursor))

        self.hlayout_2.addWidget(self.rename)
        self.hlayout_2.addWidget(self.delete)

    def show_task(self, old_text=None):
        try:
            text = self.task_input.text()
            self.name = text
            self.hlayout.removeWidget(self.task_input)
            self.task_input.deleteLater()

        except:
            pass

        self.task_name = QLabel(self.name, self)
        self.task_name.setObjectName(f"Task Name {self.index}x{self.count}")
        self.task_name.setMinimumSize(self.w*0.25*self.w_factor, self.h*0.1*self.h_factor)
        self.task_name.setFont(QFont("Arial", 10*self.h_factor))
        self.task_name.setStyleSheet("color: white;")
        self.task_name.setCursor(QCursor(Qt.IBeamCursor))
        self.task_name.setWordWrap(True)
        self.hlayout.addWidget(self.task_name)

    def btn_handler(self, command):
        if command == 'Rename':
            self.show_input()
        elif command == 'Delete':
            self.parent.delete_task(self.count, self)