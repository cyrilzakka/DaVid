from PyQt5.QtWidgets import QWidget, QSizePolicy, QGroupBox, QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from widgets.joystick import JoyStick

class RoboticControls(QWidget):
	"""
	Custom Qt Widget to group robotic controls together.
	"""
	roboticControls = pyqtSignal(tuple)

	def __init__(self, *args, **kwargs):
		super(RoboticControls, self).__init__(*args, **kwargs)
		robotic_groupbox = QGroupBox("Robotic Arm Controls")
		robotic_layout = QHBoxLayout()
		layout = QVBoxLayout()
		layout.addWidget(robotic_groupbox)

		self._lz_slider = QSlider(Qt.Vertical)
		self._lz_slider.setRange(-1, 1)
		self._lz_slider.valueChanged.connect(self.controls_moved)
		robotic_layout.addWidget(self._lz_slider)

		self._rjoystick = JoyStick()
		self._ljoystick = JoyStick()
		self._rjoystick.mouseMoved.connect(self.controls_moved)
		self._ljoystick.mouseMoved.connect(self.controls_moved)
		self._rjoystick.mouseDoubleClicked.connect(self.controls_moved)
		self._ljoystick.mouseDoubleClicked.connect(self.controls_moved)
		robotic_layout.addWidget(self._ljoystick)
		robotic_layout.addWidget(self._rjoystick)
		

		self._rz_slider = QSlider(Qt.Vertical)
		self._rz_slider.setRange(-1, 1)
		self._rz_slider.valueChanged.connect(self.controls_moved)
		robotic_layout.addWidget(self._rz_slider)
		
		robotic_groupbox.setLayout(robotic_layout)

		self.setSizePolicy(
			QSizePolicy.MinimumExpanding,
			QSizePolicy.MinimumExpanding
		)
		self.setLayout(layout)

	@pyqtSlot()
	def controls_moved(self):
		l_ang = self._ljoystick.joystickDirection()
		l_d = self._lz_slider.value()

		r_ang = self._rjoystick.joystickDirection()
		r_d = self._rz_slider.value()
		self.roboticControls.emit((l_ang, l_d, r_ang, r_d))
