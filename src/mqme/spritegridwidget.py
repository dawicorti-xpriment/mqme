# -*- coding: utf-8 *-*
from PyQt4 import QtGui


class SpriteGridWidget(QtGui.QFrame):

    def __init__(self, parent):
        super(SpriteGridWidget, self).__init__()
        self._parent = parent
        self.setGeometry(-10, -40, 500, 500)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(0, 0, 500, 500, QtGui.QColor(0, 0, 0))
        for i in range(4):
            painter.fillRect(
                (i + 1) * 100, 0, 1, 500, QtGui.QColor(255, 255, 255)
            )
            painter.fillRect(
                0, (i + 1) * 100, 500, 1, QtGui.QColor(255, 255, 255)
            )
        painter.fillRect(205, 205, 90, 90, QtGui.QColor(105, 105, 105))
        painter.end()
        super(SpriteGridWidget, self).paintEvent(event)

    def remove_image(self, image):
        self._parent.remove_image(image)

    def move_image(self, image, pos):
        self._parent.move_image(image, pos)
