from PyQt5.QtWidgets import QWidget, QShortcut, QSizePolicy, QLabel, QHBoxLayout, QSpacerItem
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QPainter, QKeySequence

class ImageViewer(QWidget):

	procDone = pyqtSignal(dict)
	playBackDone = pyqtSignal(tuple)

	def __init__(self, *args, **kwargs):
		super(ImageViewer, self).__init__(*args, **kwargs)

		image_layout = QHBoxLayout()
		self.label = QLabel(self)
		self.is_overlay_enabled = False
		self.current_image  = ''
		self.next_image = ''
		self.pixmap = QPixmap('')
		self.pixmap_overlay = QPixmap('')
		self.overlay_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
		self.overlay_shortcut.activated.connect(self.enable_overlay)

		horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum) 
		image_layout.addItem(horizontalSpacer)
		image_layout.addWidget(self.label)
		horizontalSpacer2 = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Maximum) 
		image_layout.addItem(horizontalSpacer2)
		self.setLayout(image_layout)

	def enable_overlay(self):
		self.is_overlay_enabled = not self.is_overlay_enabled
		self.on_procStart({'curr_image': self.current_image, 'overlay_frame': self.next_image})

	@pyqtSlot(dict)
	def on_procStart(self, message):

		self.current_image  = message['curr_image']
		self.next_image  = message['overlay_frame']

		self.pixmap = QPixmap(self.current_image)
		self.pixmap_overlay = QPixmap(self.next_image)
		painter = QPainter()
		painter.begin(self.pixmap)
		painter.setOpacity(0.4 if self.is_overlay_enabled else 0)
		painter.drawPixmap(0,0, self.pixmap_overlay)
		painter.end()
		self.label.setPixmap(self.pixmap)
		self.raise_()

	@pyqtSlot(tuple)
	def on_playBackStart(self, message):
		self.current_image  = message[0]
		self.next_image  = message[1]
		self.pixmap = QPixmap(self.current_image)
		self.pixmap_overlay = QPixmap(self.next_image)
		painter = QPainter()
		painter.begin(self.pixmap)
		painter.setOpacity(0.4 if self.is_overlay_enabled else 0)
		painter.drawPixmap(0,0, self.pixmap_overlay)
		painter.end()
		self.label.setPixmap(self.pixmap)
		self.raise_()
		