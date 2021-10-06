from PyQt5.QtWidgets import (QWidget, QSizePolicy, QPushButton, QHBoxLayout, 
							QShortcut, QFileDialog, QProgressDialog, QSpacerItem)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QKeySequence

import os, pathlib
import pandas as pd 
import cv2
from cv2 import VideoCapture, imwrite, resize, CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, INTER_AREA
import datetime


class PlaybackControls(QWidget):
	"""
	Custom Qt Widget to group playback controls together.
	"""
	procStart = pyqtSignal(dict)
	playBackStart = pyqtSignal(str)

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

	@pyqtSlot()  
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
			username = os.getlogin()
			suffix = username + '_' + vid_name.split('.')[0]
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

	@pyqtSlot()
	def next_frame(self):
		# Write current annotations to csv
		# Find current frame in pandas df and get the next index
		if not (self.annotation_file == '' and self.images_folder == ''):
			current_frame = os.path.basename(self.message['curr_image'])
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

	@pyqtSlot()  
	def previous_frame(self):
		# Find current frame in pandas df and get the previous index
		if not (self.annotation_file == '' and self.images_folder == ''):
			current_frame = os.path.basename(self.message['curr_image'])
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

	@pyqtSlot(tuple)
	def receiveCamControls(self, values):
		self.data_row[-2] = values[0]
		self.data_row[-1] = values[1]

	@pyqtSlot(tuple)
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
