# -*- coding: utf-8 *-*
from PyQt4 import QtGui
from PyQt4 import QtCore


class FrameImage(QtGui.QLabel):

    def __init__(self, parent, path, image_id, frame_key):
        super(FrameImage, self).__init__(parent)
        self._pixmap = QtGui.QPixmap(path)
        self._image_id = image_id
        self._parent = parent
        self._frame_key = frame_key
        self._selected = False
        self._last_pos = None

    def frame_key(self):
        return self._frame_key

    def image_id(self):
        return self._image_id

    def ratio(self):
        return (
            self._pixmap.width() / 32.0, self._pixmap.height() / 32.0
        )

    def resizeEvent(self, event):
        self.setPixmap(self._pixmap.scaled(self.width(), self.height()))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self._parent.remove_image(self)
        else:
            self._selected = True
            self._last_pos = (event.globalX(), event.globalY())
            self.setStyleSheet('QWidget {border : 1px dotted blue;}')

    def mouseMoveEvent(self, event):
        if self._selected:
            last_x, last_y = self._last_pos
            self._parent.move_image(self, (
                event.globalX() - last_x,
                event.globalY() - last_y
            ))
            self._last_pos = (event.globalX(), event.globalY())

    def mouseReleaseEvent(self, event):
        self._selected = False
        self.setStyleSheet('QWidget {border : none;}')
