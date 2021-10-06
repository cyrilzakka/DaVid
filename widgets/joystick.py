from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import pyqtSignal, QPointF, QRectF, QLineF, Qt
from PyQt5.QtGui import QPainter, QColor
from enum import Enum

class Direction(Enum):
	Left = 0
	Right = 1
	Up = 2
	Down = 3

class JoyStick(QWidget):

	mouseMoved = pyqtSignal(float)
	mouseDoubleClicked = pyqtSignal()

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
