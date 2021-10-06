from PyQt5.QtWidgets import QWidget, QSizePolicy, QGroupBox, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

class MiscPanel(QWidget):
	"""
	Custom Qt Widget to display misc video information together.
	"""
	procDone = pyqtSignal(dict)

	def __init__(self, *args, **kwargs):
		super(MiscPanel, self).__init__(*args, **kwargs)
		info_groupbox = QGroupBox("Media Information")
		info_layout = QVBoxLayout()
		layout = QVBoxLayout()
		layout.addWidget(info_groupbox)
		
		self.video_name = QLabel("Name: ")
		self.video_name.setWordWrap(True)
		self.video_frames = QLabel("Viewing frame: ")
		self.video_size = QLabel("Size: ")
		self.video_loc = QLabel("Location:")
		self.video_loc.setWordWrap(True)
		self.video_dur = QLabel("Duration: ")

		info_layout.addWidget(self.video_name)
		info_layout.addWidget(self.video_frames)
		info_layout.addWidget(self.video_size)
		info_layout.addWidget(self.video_loc)
		info_layout.addWidget(self.video_dur)
		info_groupbox.setLayout(info_layout)

		self.setSizePolicy(
			QSizePolicy.Maximum,
			QSizePolicy.MinimumExpanding
		)
		self.setLayout(layout)

	@pyqtSlot(dict)
	def on_procStart(self, message):
		vid_location, vid_name  = message['filepath'].rsplit('/', 1)
		self.video_name.setText(f"Name: {vid_name}")
		self.video_loc.setText(f"Location: {vid_location}")
		self.video_frames.setText(f"Viewing frame: {message['curr_frame_index']+1} of {message['count']}")
		self.video_dur.setText(f"Duration: {message['duration']}")
		self.video_size.setText(f"Size: {message['size']}")
		self.raise_()
