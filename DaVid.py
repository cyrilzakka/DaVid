import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
							QSpacerItem, QSizePolicy)
from widgets import ImageViewer, CameraControls, RoboticControls, PlaybackControls, MiscPanel

class MainWindow(QMainWindow):

	def __init__(self):
		super(MainWindow, self).__init__()
		self.setWindowTitle("DaVinci Action Annotator")
		modular_layout = QVBoxLayout()
		control_layout = QHBoxLayout()
		
		self.imageViewer = ImageViewer()
		modular_layout.addWidget(self.imageViewer)

		horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum) 
		control_layout.addItem(horizontalSpacer)

		camera_controls = CameraControls()
		robotic_controls = RoboticControls()

		control_layout.addWidget(robotic_controls)
		control_layout.addWidget(camera_controls)

		self.misc = MiscPanel()
		control_layout.addWidget(self.misc)
		horizontalSpacer2 = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum) 
		control_layout.addItem(horizontalSpacer2)
		modular_layout.addLayout(control_layout)
		
		self.playback_controls = PlaybackControls()
		modular_layout.addWidget(self.playback_controls)

		self.playback_controls.procStart.connect(self.misc.on_procStart)
		self.playback_controls.procStart.connect(self.imageViewer.on_procStart)
		self.playback_controls.playBackStart.connect(self.imageViewer.on_playBackStart)

		camera_controls.camControls.connect(self.playback_controls.receiveCamControls)
		robotic_controls.roboticControls.connect(self.playback_controls.receiveRoboticControls)

		widget = QWidget()
		widget.setLayout(modular_layout)
		self.setCentralWidget(widget)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	app.exec()