import sys, os, pathlib
from enum import Enum
import datetime
import pandas as pd 
import cv2
from cv2 import VideoCapture, imwrite, resize, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, INTER_AREA

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
							QVBoxLayout, QHBoxLayout, QPushButton, 
							QSpacerItem, QSizePolicy, QSlider, 
							QGroupBox, QLabel, QFileDialog, QProgressDialog, QShortcut)
from PyQt5.QtGui import QColor, QPixmap, QPainter, QKeySequence
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF, QThread


# Modules should probably be in a different file but ain't nobody got time for that.
# TODO: Separate GUI from logic

class ImageViewer(QWidget):

	procDone = QtCore.pyqtSignal(dict)
	playBackDone = QtCore.pyqtSignal(str)

	def __init__(self, *args, **kwargs):
		super(ImageViewer, self).__init__(*args, **kwargs)

		image_layout = QHBoxLayout()
		self.label = QLabel(self)
		self.pixmap = QPixmap('').scaled(760, 380, Qt.KeepAspectRatio)
		self.label.setPixmap(self.pixmap)
		self.label.setScaledContents(True)
		horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum) 
		image_layout.addItem(horizontalSpacer)
		image_layout.addWidget(self.label)
		horizontalSpacer2 = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum) 
		image_layout.addItem(horizontalSpacer2)
		self.setLayout(image_layout)

	@QtCore.pyqtSlot(dict)
	def on_procStart(self, message):
		current_image  = message['curr_image']
		self.label.setPixmap(QPixmap(current_image).scaled(760, 380, Qt.KeepAspectRatio))
		self.raise_()

	@QtCore.pyqtSlot(str)
	def on_playBackStart(self, message):
		self.label.setPixmap(QPixmap(message).scaled(760, 380, Qt.KeepAspectRatio))
		self.raise_()

class PlaybackControls(QWidget):
	"""
	Custom Qt Widget to group playback controls together.
	"""
	procStart = QtCore.pyqtSignal(dict)
	playBackStart = QtCore.pyqtSignal(str)

	def __init__(self, *args, **kwargs):
		super(PlaybackControls, self).__init__(*args, **kwargs)
		self.message = {}
		self.annotation_file = ''
		self.images_folder = ''
		self.data_row = [0,0,0,0,0,0]

		playback_layout = QHBoxLayout()


		self.previousButton = QPushButton('Previous frame')
		self.previousButton.clicked.connect(self.previous_frame)
		self.prev_shortcut = QShortcut(QKeySequence("left"), self)
		self.prev_shortcut.activated.connect(self.previous_frame)


		self.nextButton = QPushButton('Next frame')
		self.nextButton.clicked.connect(self.next_frame)
		self.next_shortcut = QShortcut(QKeySequence("right"), self)
		self.next_shortcut.activated.connect(self.next_frame)


		playback_layout.addWidget(self.previousButton)
		playback_layout.addWidget(self.nextButton)
				
		horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum) 
		playback_layout.addItem(horizontalSpacer)

		importB = QPushButton('Import video')
		importB.clicked.connect(self.load_video)
		playback_layout.addWidget(importB)

		self.setSizePolicy(
			QSizePolicy.MinimumExpanding,
			QSizePolicy.Maximum,
		)
		self.setLayout(playback_layout)

	@QtCore.pyqtSlot()  
	def load_video(self):
		filename, _ = QFileDialog.getOpenFileName(self, 'Open a file', '', 'Video Files (*.avi *.mp4 *.flv *.mov *.m4v)')
		if filename != '':
			self.message['filepath'] = filename
			vidcap = VideoCapture(filename)
			fps = vidcap.get(CAP_PROP_FPS)  
			frame_count = int(vidcap.get(CAP_PROP_FRAME_COUNT))
			duration = frame_count/fps
			_, vid_name  = filename.rsplit('/', 1)

			self.message['size'] = self.sizeof_fmt(os.path.getsize(filename))
			self.message['duration'] = datetime.timedelta(seconds=round(duration%60))
			self.message['count'] = str(frame_count)
			self.message['curr_frame_index'] = 0
			vidcap.release()

			# House cleaning
			desktop_path = pathlib.Path.home() / 'Desktop'
			_, username = str(pathlib.Path.home()).rsplit('/', 1)
			suffix = username + '_' + vid_name.split('.')[0] + '_'
			data_folder = os.path.join(desktop_path, 'annotated_data')
			self.images_folder = os.path.join(data_folder, 'images')
			self.annotation_file = os.path.join(data_folder, 'annotations.csv')

			# Create data folder
			if not os.path.exists(data_folder):
				os.mkdir(data_folder)
			
				# Create images folder
				if not os.path.exists(self.images_folder):
					os.mkdir(self.images_folder)

				# Create csv file
				with open(self.annotation_file, "a") as _:
					pass

			# Extract images
			if not self.isAlreadyExtracted(suffix):
				# Show and animate progress bar
				self.progress = QProgressDialog("Extracting frames...", '', 0, frame_count)
				self.progress.setValue(0)
				self.progress.setCancelButton(None)
				self.progress.setWindowModality(Qt.WindowModal)
				self.progress.show()
				self.extractImages(filename, self.images_folder, suffix, self.annotation_file)

			# Set first image
			rec_index, rec_img = self.getRecentFrame()
			first_img = os.path.join(self.images_folder, rec_img)
			self.message['curr_image'] = first_img
			self.message['curr_frame_index'] = rec_index
			self.procStart.emit(self.message)

	@QtCore.pyqtSlot()
	def next_frame(self):
		# Write current annotations to csv
		# Find current frame in pandas df and get the next index
		if not (self.annotation_file == '' and self.images_folder == ''):
			_, current_frame = self.message['curr_image'].rsplit('/', 1)
			df = pd.read_csv(self.annotation_file)
			curr_index = df.loc[df['frame'] == current_frame].index[0]
			df.iloc[curr_index] = pd.Series({'frame': current_frame, 'left_ang': self.data_row[0],'left_d': self.data_row[1],'right_ang': self.data_row[2],'r_ang': self.data_row[3],'cam_ang': self.data_row[4],'cam_d': self.data_row[5]})
			if curr_index + 1 < len(df):
				next_frame = df.iloc[curr_index + 1].frame
				fimg = os.path.join(self.images_folder, next_frame)
				self.message['curr_image'] = fimg
				self.message['curr_frame_index'] = self.message['curr_frame_index'] + 1
			else:
				next_frame = current_frame
				fimg = os.path.join(self.images_folder, next_frame)
				self.message['curr_image'] = fimg
			df.to_csv(self.annotation_file, index = False)
			self.procStart.emit(self.message)
			self.playBackStart.emit(os.path.join(self.images_folder,next_frame))

	@QtCore.pyqtSlot()  
	def previous_frame(self):
		# Find current frame in pandas df and get the previous index
		if not (self.annotation_file == '' and self.images_folder == ''):
			_, current_frame = self.message['curr_image'].rsplit('/', 1)
			df = pd.read_csv(self.annotation_file)
			curr_index = df.loc[df['frame'] == current_frame].index[0]
			df.iloc[curr_index] = pd.Series({'frame': current_frame, 'left_ang': self.data_row[0],'left_d': self.data_row[1],'right_ang': self.data_row[2],'right_d': self.data_row[3],'cam_ang': self.data_row[4],'cam_d': self.data_row[5]})
			if curr_index - 1 >= 0:
				prev_frame = df.iloc[curr_index - 1].frame
				fimg = os.path.join(self.images_folder, prev_frame)
				self.message['curr_image'] = fimg
				self.message['curr_frame_index'] = self.message['curr_frame_index'] - 1
			else:
				prev_frame = current_frame
				fimg = os.path.join(self.images_folder, prev_frame)
				self.message['curr_image'] = fimg
			df.to_csv(self.annotation_file, index = False)
			self.procStart.emit(self.message)
			self.playBackStart.emit(os.path.join(self.images_folder,prev_frame))

	@QtCore.pyqtSlot(tuple)
	def receiveCamControls(self, values):
		self.data_row[-2] = values[0]
		self.data_row[-1] = values[1]

	@QtCore.pyqtSlot(tuple)
	def receiveRoboticControls(self, values):
		self.data_row[0] = values[0]
		self.data_row[1] = values[1]
		self.data_row[2] = values[2]
		self.data_row[3] = values[3]
	
	def isAlreadyExtracted(self, suffix):
		# Lazy way to check if frames already extracted.
		# Should eventually be changed to checking CSV file using pandas
		return os.path.isfile(os.path.join(self.images_folder, f'{suffix}_frame0.png'))

	def getRecentFrame(self):
		# Check most recent frame without annotations or return first frame
		df = pd.read_csv(self.annotation_file)
		empty = df[df.left_ang.isna()]
		if len(empty) > 0:	
			return empty.index[0], empty.iloc[0]['frame']
		else:
			# TODO: Raise error. All frames have been annotated
			return ''

	def extractImages(self, pathIn, pathOut, suffix, csv, t=30):
		'''
		Extract frame from video every t seconds
		'''
		cap = cv2.VideoCapture(pathIn)
		fps = round(cap.get(cv2.CAP_PROP_FPS))
		hop = round(fps / t)
		curr_frame = 0
		with open(csv, 'a') as file:
			file.write('frame,left_ang,left_d,right_ang,right_d,cam_ang,cam_d')
			file.write('\n')
			while(True):
				ret, frame = cap.read()
				if not ret: 
					break
				width = int(frame.shape[1] * 50 / 100)
				height = int(frame.shape[0] * 50 / 100)

				if curr_frame % hop == 0:
					output = resize(frame, (width, height), interpolation = INTER_AREA)
					name = suffix + "_frame%d.png" % curr_frame
					cv2.imwrite(pathOut + "/"+ name, output)
					file.write(name)
					file.write('\n')
					curr_frame += 1
					self.progress.setValue(curr_frame)
			file.close()
			
		cap.release()

	def sizeof_fmt(self, num, suffix="B"):
		for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
			if abs(num) < 1024.0:
				return f"{num:3.1f}{unit}{suffix}"
			num /= 1024.0
		return f"{num:.1f}Yi{suffix}"

class CameraControls(QWidget):
	"""
	Custom Qt Widget to group camera controls together.
	"""

	camControls = QtCore.pyqtSignal(tuple)

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

	@QtCore.pyqtSlot()
	def controls_moved(self):
		angle = self._joystick.joystickDirection()
		z_value = self._z_slider.value()
		self.camControls.emit((z_value, angle))

class Direction(Enum):
	Left = 0
	Right = 1
	Up = 2
	Down = 3

class JoyStick(QWidget):

	mouseMoved = QtCore.pyqtSignal(float)
	mouseDoubleClicked = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		super(JoyStick, self).__init__(parent)
		self.setMinimumSize(100, 100)
		self.movingOffset = QPointF(0, 0)
		self.grabCenter = False
		self.__maxDistance = 30
		self.setSizePolicy(
			QSizePolicy.Minimum,
			QSizePolicy.Minimum
		)

	def paintEvent(self, event):
		painter = QPainter(self)
		bounds = QRectF(-self.__maxDistance, -self.__maxDistance, self.__maxDistance * 2, self.__maxDistance * 2).translated(self._center())
		painter.setBrush(QColor(215, 215, 215, 255))
		painter.setPen(QColor(215, 215, 215, 0))
		painter.drawEllipse(bounds)
		painter.setBrush(Qt.white)
		painter.drawEllipse(self._centerEllipse())

	def _centerEllipse(self):
		if self.grabCenter:
			return QRectF(-20, -20, 40, 40).translated(self.movingOffset)
		return QRectF(-20, -20, 40, 40).translated(self._center())

	def _center(self):
		return QPointF(self.width()/2, self.height()/2)

	def _boundJoystick(self, point):
		limitLine = QLineF(self._center(), point)
		if (limitLine.length() > self.__maxDistance):
			limitLine.setLength(self.__maxDistance)
		return limitLine.p2()

	def joystickDirection(self):
		if not self.grabCenter:
			return 0
		normVector = QLineF(self._center(), self.movingOffset)
		currentDistance = normVector.length()
		angle = normVector.angle()
		return angle
		# distance = min(currentDistance / self.__maxDistance, 1.0)
		# if 45 <= angle < 135:
		# 	return (Direction.Up, distance, angle)
		# elif 135 <= angle < 225:
		# 	return (Direction.Left, distance, angle)
		# elif 225 <= angle < 315:
		# 	return (Direction.Down, distance, angle)
		# return (Direction.Right, distance, angle)

	def mousePressEvent(self, ev):
		self.grabCenter = self._centerEllipse().contains(ev.pos())
		return super().mousePressEvent(ev)

	def mouseDoubleClickEvent(self, event):
		self.grabCenter = False
		self.movingOffset = QPointF(0, 0)
		self.update()
		self.mouseDoubleClicked.emit()
		event.accept()

	def mouseReleaseEvent(self, event):
		pass

	def mouseMoveEvent(self, event):
		if self.grabCenter:
			self.movingOffset = self._boundJoystick(event.pos())
			self.update()
			self.mouseMoved.emit(self.joystickDirection())
			event.accept()

class RoboticControls(QWidget):
	"""
	Custom Qt Widget to group robotic controls together.
	"""
	roboticControls = QtCore.pyqtSignal(tuple)

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

	@QtCore.pyqtSlot()
	def controls_moved(self):
		l_ang = self._ljoystick.joystickDirection()
		l_d = self._lz_slider.value()

		r_ang = self._rjoystick.joystickDirection()
		r_d = self._rz_slider.value()
		self.roboticControls.emit((l_ang, l_d, r_ang, r_d))

class MiscPanel(QWidget):
	"""
	Custom Qt Widget to display misc video information together.
	"""
	procDone = QtCore.pyqtSignal(dict)

	def __init__(self, *args, **kwargs):
		super(MiscPanel, self).__init__(*args, **kwargs)
		info_groupbox = QGroupBox("Media Information")
		info_layout = QVBoxLayout()
		layout = QVBoxLayout()
		layout.addWidget(info_groupbox)
		
		self.video_name = QLabel("Name: ")
		self.video_name.setWordWrap(True)
		self.video_frames = QLabel("Frames: ")
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

	@QtCore.pyqtSlot(dict)
	def on_procStart(self, message):
		vid_location, vid_name  = message['filepath'].rsplit('/', 1)
		self.video_name.setText(f"Name: {vid_name}")
		self.video_loc.setText(f"Location: {vid_location}")
		self.video_frames.setText(f"Frame {message['curr_frame_index']+1} of {message['count']}")
		self.video_dur.setText(f"Duration: {message['duration']}")
		self.video_size.setText(f"Size: {message['size']}")
		self.raise_()

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