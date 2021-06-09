from PyQt5.QtWidgets import QAbstractSpinBox, QSizePolicy, QSpacerItem, QHBoxLayout, QDialog, QApplication, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from widgets import save, restore, PushButton, InputBox

class Settings(QDialog):
	"""Settings Ui"""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setObjectName("Pomodoro")
		self.parent = parent
		self.settings = restore("Pomodoro")
		self.init_ui()

	def init_ui(self):
		#Setting up ui component
		widget = QWidget(self)
		mlayout = QVBoxLayout()

		self.title = QLabel("Settings", self)
		self.work_time = (QLabel("Work Time (minutes)", self), InputBox("SpinBox", self))
		self.short_time = (QLabel("Short Time (minutes)"), InputBox("SpinBox", self))
		self.long_time = (QLabel("Long Time (minutes)"), InputBox("SpinBox", self))
		self.auto_start = (QLabel("Auto Start Round"), InputBox("ComboBox", self))
		self.break_interval = (QLabel("Break Interval"), InputBox("SpinBox", self))

		self.save_btn = PushButton("Ok", self)
		self.save_btn.clicked.connect(self.closeEvent)
		self.save_btn.setStyleSheet("""border: 1px solid gray;""")
		self.save_btn.setFixedSize(60, 20)
		self.title.setFont(QFont("Arial", 20))

		mlayout.addWidget(self.title, alignment=Qt.AlignHCenter)
		for index, name in enumerate(('work_time', 'short_time', 'long_time', 'auto_start','break_interval')):
			value = self.settings.get(name)
			name = eval(f"self.{name}")

			if name[1].input_type == 'SpinBox':
				name[1].widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
				name[1].widget.setValue(value)
			else:
				name[1].widget.addItem('True')
				name[1].widget.addItem('False')
				name[1].widget.setCurrentText(str(value))

			hlayout = QHBoxLayout()
			name[0].setFont(QFont('Bahnschrift Light', 12))
			hlayout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
			hlayout.addWidget(name[0])
			hlayout.addWidget(name[1].widget)
			hlayout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))

			mlayout.addItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
			mlayout.addLayout(hlayout)
			mlayout.addItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))

		mlayout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
		mlayout.addWidget(self.save_btn, alignment=Qt.AlignHCenter)
		mlayout.addItem(QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
		widget.setObjectName("Widget")
		widget.setStyleSheet("""
							 #Widget{
							 	 background-color: palette(window);
    							 border-radius: 18px;
    							 border: 1px solid gray;
							}
							""")
		widget.setFixedSize(420, 380)
		widget.setLayout(mlayout)
		save(self)

	def closeEvent(self, event):
		#Saving and updating the settings
		save(self)
		self.hide()

		for name in ('Work', 'Short', 'Long'):
			self.parent.m_pages[name].update_changes()