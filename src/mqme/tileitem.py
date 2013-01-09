# -*- coding: utf-8 *-*
from PyQt4 import QtGui
from PyQt4 import QtCore

import os
import settings


class TileItem(QtGui.QLabel):

    def __init__(self, parent, queue, x, y, width=None, height=None):
        super(TileItem, self).__init__(parent)
        self._queue = queue
        self._pixmap = QtGui.QPixmap(os.path.join(
            settings.IMAGES_PATH, 'tile_selection.png'
        ))
        self._parent = parent
        if width and height:
            self._x = x
            self._y = y
            self._width = width
            self._height = height
        else:
            self._x = x * self._parent.pixmap().width() / self._parent.width()
            self._y = y * self._parent.pixmap().height(
            ) / self._parent.height()
            self._width = 1
            self._height = 1
            self._queue.put({
                'name': 'picture.mousemove',
                'x': self._x,
                'y': self._y,
                'width': self._width,
                'height': self._height
            })
        self.update_geometry()
        self._name = ''

    def set_name(self, name):
        self._name = name

    def update_geometry(self):
        self.setGeometry(
            self._x * self._parent.width() / self._parent.pixmap().width(),
            self._y * self._parent.height() / self._parent.pixmap().height(),
            self._width * self._parent.width() / self._parent.pixmap().width(),
            self._height * self._parent.height(
            ) / self._parent.pixmap().height()
        )
        rect = self.geometry()
        self.setPixmap(self._pixmap.scaled(rect.width(), rect.height()))

    def set_size(self, width, height):
        self._width = width * self._parent.pixmap(
        ).width() / self._parent.width()
        self._height = height * self._parent.pixmap(
        ).height() / self._parent.height()
        self.update_geometry()
        self._queue.put({
            'name': 'picture.mousemove',
            'x': self._x,
            'y': self._y,
            'width': self._width,
            'height': self._height
        })

    def real_width(self):
        return self._width

    def to_dict(self):
        return {
            'name': self._name,
            'crop_x': self._x,
            'crop_y': self._y,
            'crop_width': self._width,
            'crop_height': self._height
        }

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self._parent.remove_item(self)
