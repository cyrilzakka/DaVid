from PyQt5.QtWidgets import QWidget, QSizePolicy, QLabel, QHBoxLayout, QSpacerItem
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap

class ImageViewer(QWidget):

	procDone = pyqtSignal(dict)
	playBackDone = pyqtSignal(str)

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

	@pyqtSlot(dict)
	def on_procStart(self, message):
		current_image  = message['curr_image']
		self.label.setPixmap(QPixmap(current_image).scaled(760, 380, Qt.KeepAspectRatio))
		self.raise_()

	@pyqtSlot(str)
	def on_playBackStart(self, message):
		self.label.setPixmap(QPixmap(message).scaled(760, 380, Qt.KeepAspectRatio))
		self.raise_()
