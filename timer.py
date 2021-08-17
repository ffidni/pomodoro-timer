from time import sleep
from pygame import mixer
from settings import *
from menu import *
from todolist import *
from Styles.styles import (TEXT_STYLE, COUNTDOWN_STYLE, BTN_STYLE)
from PyQt5.QtCore import pyqtSlot, QThread

class Timer(MainWindow):
    """Timer(MainWindoww) -> Timer's page"""

    resume_time = 0
    is_stopped = False
    is_back = False
    work_counter = 0
    current_timer = ""

    def __init__(self, timer_name, parent=None):
        super().__init__()
        self.parent = parent
        self.current_timer = timer_name
        self.timer_name = 'Work Time!' if self.current_timer == 'Work' else 'Break Time!'

        #Create an instance called thread to the TimerThread class
        self.thread = TimerThread(seconds=0)

    def init_ui(self):
        super().init_ui()
        #Declaring all timer's time in seconds
        self.timer_times = {"Work":25, "Short":5, "Long":10}
        self.auto_start = False
        self.break_interval = 3
        QTimer.singleShot(100, self.update_changes)
        self.installEventFilter(self)

    def setup_label(self):
        self.title = QLabel(self.timer_name, self)
        self.timer_widget = QWidget(self)
        self.timer_layout = QHBoxLayout()
        self.timer_count = QLabel(self.timer_widget)

        self.title.setStyleSheet(TEXT_STYLE)
        self.timer_widget.setMaximumSize(265, 121)
        self.timer_layout.setContentsMargins(0, 0, 0, 0)
        self.timer_count.setStyleSheet(COUNTDOWN_STYLE)
        self.todolist_btn = PushButton(self)
        self.left_spacer = QSpacerItem(42, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.center_spacer = QSpacerItem(0, 70, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.bottom_spacer = QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.top_spacer = QSpacerItem(0, 70, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.todolist_btn.setIcon(QIcon("Assets/IMG/task.png"))
        self.todolist_btn.setIconSize(QSize(28, 28))
        self.todolist_btn.setStyleSheet("""background-color: transparent;""")
        self.todolist_btn.setToolTip("Open Todolist App")
        self.todolist_btn.clicked.connect(lambda: self.button_handler("todolist"))

        self.timer_layout.setSpacing(5)
        self.timer_layout.addItem(self.left_spacer)
        self.timer_layout.addWidget(self.timer_count)
        self.timer_layout.addWidget(self.todolist_btn)

        self.label_layout.addItem(self.top_spacer)
        self.label_layout.addWidget(self.title, alignment=Qt.AlignHCenter)
        self.label_layout.addItem(self.center_spacer)
        self.label_layout.addLayout(self.timer_layout)
        self.label_layout.addWidget(self.timer_widget)
        self.label_layout.addItem(self.bottom_spacer)
        self.label_layout.setSpacing(0)
        self.label_layout.setContentsMargins(0, 0, 0, 0)

    def setup_button(self):
        #Setting up options buttons

        tab = '\t'*6
        self.current_run_text = "Start"
        self.start_text, self.stop_text = f"{tab}Start{tab}", f"{tab}Stop{tab}"

        self.btn_back= PushButton(f"{tab}Back{tab}", self, clicked=lambda: self.button_handler("Back"))
        self.btn_run = PushButton(f"{tab}Start{tab}", self, clicked=lambda: self.button_handler(self.current_run_text))
        self.btn_settings = PushButton(f"\t\t Settings \t\t", self, clicked=lambda: self.button_handler("Settings"))
        self.side_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.btn_spacer = QSpacerItem(20,10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.btn_container.layout().addItem(self.side_spacer)
        for i in ('back', 'run', 'settings'):
            eval(f"self.btn_{i}.setFont(QFont('Bahnschrift Light', 14))")
            eval(f"self.btn_{i}.setStyleSheet(BTN_STYLE)")
            eval(f"self.btn_container.layout().addWidget(self.btn_{i})")
            if i != 'settings':
                self.btn_container.layout().addItem(self.btn_spacer)

        self.btn_container.layout().addItem(self.side_spacer)

    def resizeEvent(self, events):
        self.w_factor = self.rect().width() / self.w
        self.h_factor = self.rect().height() / self.h

        self.title.setFont(QFont("Arial", 35*self.h_factor, 75))
        self.timer_count.setFont(QFont("Arial", 74*self.h_factor))
        self.timer_widget.setMaximumSize(self.w*self.w_factor, self.h*0.25*self.h_factor)
        self.center_spacer.changeSize(0, 72*self.h_factor)
        self.bottom_spacer.changeSize(0, 18*self.h_factor)
        self.left_spacer.changeSize(34*self.w_factor, 0)
        self.top_spacer.changeSize(0, 70*self.h_factor)
        self.todolist_btn.setIconSize(QSize(28*self.w_factor, 28*self.h_factor))

        for i in ('back', 'run', 'settings'):
            eval(f"self.btn_{i}.setMaximumHeight(51*self.h_factor)")
            eval(f"self.btn_{i}.setFont(QFont('Bahnschrift Light', 14*self.h_factor))")
            eval(f"self.btn_{i}.setStyleSheet(BTN_STYLE.format(4*self.h_factor, 5*self.h_factor))")

    def mousePressEvent(self, event):
        if not self.parent.m_pages["Settings"].isHidden():
            self.parent.m_pages["Settings"].close()

    def make_timer_format(self, seconds):
        mins, secs = divmod(seconds, 60)
        return "{:02d}:{:02d}".format(mins, secs)

    def show_todolist(self):
        self.todolist_ui = self.parent.m_pages["Todolist"]
        self.todolist_ui.closeEvent = self.todolistCloseEvent

        if self.todolist_ui.isHidden():
            self.todolist_ui.show()
        else:
            self.todolist_ui.hide()
            QTimer.singleShot(10, self.todolist_ui.show)

        if not self.todolist_ui.settings:
            self.todolist_ui.first = False
            self.todolist_ui.new_task()
        elif self.todolist_ui.settings['Tabs'] >= 0:
            self.todolist_ui.first = False
            self.todolist_ui.new_task()

    def button_handler(self, command):
        if not self.parent.m_pages["Settings"].isHidden():
            self.close()

        if command == 'Back':
            self.reset_timer()
            self.goto("Main")
        elif command == 'Start': 
            self.start_timer()
        elif command == 'Stop': 
            self.stop_timer()
        elif command == 'Settings':
            self.parent.m_pages["Settings"].show()
        elif command == 'todolist':
            self.show_todolist()

    def update_changes(self):
        values = restore("Pomodoro")
        for key in values:
            name = key[:-5].capitalize()
            if name in self.timer_times:
                self.timer_times[key[:-5].capitalize()] = values[key]*60
                is_running = self.parent.m_pages[name].thread.isRunning()
                is_stopped = self.parent.m_pages[name].is_stopped
                if not is_running and not is_stopped:
                    self.parent.m_pages[name].timer_count.setText("{:02d}:00".format(values[key]))
            elif key == 'auto_start':
                self.auto_start = values[key]
            else:
                self.break_interval = values[key]

    def todolistCloseEvent(self, event):
        self.todolist = False
        save(self.todolist_ui, self.todolist_ui.subtasks)

    def reset_timer(self):
        self.resume_time = 0
        self.is_stopped = False
        self.is_back = True
        self.current_run_text = "Start"
        self.btn_run.setText(self.start_text)
        self.thread.stop()
        self.change_countdown(self.timer_times[self.current_timer])

    def stop_timer(self):
        self.is_stopped = True
        self.thread.stop()
        self.current_run_text = "Start"
        self.btn_run.setText(self.start_text)

    def resume_save(self, seconds):
        #Save resume time in seconds to the class attribute
        self.resume_time = seconds

    def change_countdown(self, countdown):
        timer_count = self.make_timer_format(countdown)
        self.timer_count.setText(timer_count)

    def resume_handler(self):
        #Adding current timer's name to self.current_timer attribute
        #self.current_timer = self.title.text()

        #Check if there is resume time, use them if they're exists, otherwise we're gonna use the default time
        seconds = None
        if self.resume_time and self.is_stopped:
            seconds = self.resume_time
            self.resume_time = 0
        else:
            seconds = self.timer_times[self.current_timer]
        return seconds

    @pyqtSlot()
    def start_timer(self):
        def start_thread(seconds):
            self.thread = TimerThread(seconds=seconds)
            self.thread.start()

            #Receiving the seconds from the countdown thread and display them
            self.thread.seconds_signal.connect(self.change_countdown)

            #When the timer is over, go to finished handler method
            self.thread.finished.connect(self.finished_handler)

            #When the timer is stopped, receive and save the current seconds
            self.thread.resume.connect(self.resume_save)

        #Get the time in seconds from resume_handler and pass them to the thread
        seconds = self.resume_handler()
        self.current_run_text = "Stop"
        self.btn_run.setText(self.stop_text)
        self.is_stopped = False
        self.is_back = False
        start_thread(seconds)

    def timer_counter_handler(self):
        #Check the work counter, to choose the best break for user when the work timer ends
        work_current = self.parent.m_pages["Work"].current_timer
        if self.current_timer == "Work":
            #If you work less than 3 times, then short break is for you
            self.work_counter += 1
            if self.work_counter < self.break_interval:
                work_current = "Short"

            #Otherwise, please take a long break!
            else:
                self.work_counter = 0
                work_current = "Long"
        else:
            work_current = "Work"

        self.parent.m_pages["Work"].current_timer = work_current
        self.goto(work_current)
        if self.auto_start:
            self.parent.m_pages[work_current].start_timer()

    @pyqtSlot()
    def finished_handler(self):
        #Events when the timer ends
        if not self.resume_time and not self.is_stopped and not self.is_back:
            self.change_countdown(self.timer_times[self.current_timer])
            self.timer_counter_handler()
            self.current_run_text = "Start"
            self.btn_run.setText(self.start_text)
            self.notifications = Notifications(self, self.parent.m_pages["Work"].current_timer)
            self.notifications.show()
            self.notifications.ring_the_bell()
            QTimer.singleShot(5000, self.notifications.close)

class TimerThread(QThread):
    """TimerThread(QThread) -> Timer's countdown thread"""

    #Declaring signals for sending values between classes
    seconds_signal = pyqtSignal(int)
    resume = pyqtSignal(int)

    def __init__(self, seconds=0):
        super().__init__()
        self.seconds = seconds+1

    def run(self):
        #Start the countdown
        while (self.seconds > 0):
            self.seconds -= 1
            self.seconds_signal.emit(self.seconds)
            sleep(1)

    def stop(self):
        #When the countdown is stopped, send the resume value to the connected signal (Timer().resume_save)
        self.terminate()
        self.resume.emit(self.seconds)

class Notifications(QMainWindow):
    """Notifications(QMainWindow) -> Notifications popup gui"""

    def __init__(self, parent, current_timer):
        super().__init__()
        self.parent = parent

        #Setting up ui components
        self.current_timer = current_timer

        #Remove window's borders
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(326, 113)

        #Get the desktop's resolution and put the gui to the bottom right of the screen
        current_size = self.frameGeometry()
        monitor_size = QDesktopWidget().availableGeometry()
        current_size.moveRight(monitor_size.right())
        self.move(current_size.x(), monitor_size.bottom()-135)

        self.init_ui()

    def init_ui(self):
        self.icon = PushButton(self)
        self.title = QLabel("Pomodoro Timer", self)
        text = f"Time to {f'take a {self.current_timer} break' if self.current_timer in 'Short Long' else 'Work'} !"
        self.text = QLabel(text, self)

        self.icon.setIcon(QIcon("Assets/IMG/small_icon.png"))
        self.icon.setGeometry(QRect(70, 23, 25, 25))
        self.icon.setIconSize(QSize(25, 25))
        self.icon.setCursor(QCursor(Qt.ArrowCursor))
        self.icon.setStyleSheet("""background-color: transparent;
                                   border; none;""")
        self.title.setFont(QFont("Bahnschrift Light", 14))
        self.title.setGeometry(QRect(110, 20, 141, 31))
        self.text.setFixedSize(290, 31)
        self.text.setFont(QFont("Bahnschrift Light", 15))
        self.text.move(15, 60)
        self.text.setAlignment(Qt.AlignCenter)

    def ring_the_bell(self):
        mixer.init()
        bell_sounds = mixer.Sound("Assets/SOUNDS/bell.mp3")
        bell_sounds.set_volume(0.4)
        bell_sounds.play()

    def mousePressEvent(self, event):
        self.close()
        self.parent.parent.close()
        self.parent.parent.show()