from PyQt5.QtWidgets import QWidget, QSizePolicy, QGroupBox, QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from widgets.joystick import JoyStick

class CameraControls(QWidget):
	"""
	Custom Qt Widget to group camera controls together.
	"""

	camControls = pyqtSignal(tuple)

	def __init__(self, *args, **kwargs):
		super(CameraControls, self).__init__(*args, **kwargs)
		camera_groupbox = QGroupBox("Camera Controls")
		camera_layout = QHBoxLayout()
		layout = QVBoxLayout()
		layout.addWidget(camera_groupbox)
		
		self._joystick = JoyStick()
		self._joystick.mouseMoved.connect(self.controls_moved)
		self._joystick.mouseDoubleClicked.connect(self.controls_moved)

		self._z_slider = QSlider(Qt.Vertical)
		self._z_slider.setRange(-1, 1)
		self._z_slider.valueChanged.connect(self.controls_moved)
		camera_layout.addWidget(self._z_slider)
		camera_layout.addWidget(self._joystick)
		camera_groupbox.setLayout(camera_layout)

		self.setSizePolicy(
			QSizePolicy.Maximum,
			QSizePolicy.MinimumExpanding
		)
		self.setLayout(layout)

	@pyqtSlot()
	def controls_moved(self):
		angle = self._joystick.joystickDirection()
		z_value = self._z_slider.value()
		self.camControls.emit((angle, z_value))
