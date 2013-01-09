# -*- coding: utf-8 *-*
import os
from PyQt4 import QtGui

import settings

from mqme.config import Config


class MapGridItem(QtGui.QLabel):

    def __init__(self, parent, map_name, x, y):
        super(MapGridItem, self).__init__(parent)
        self._x = x
        self._y = y
        self._pixmap = None
        self._special = None
        camera_width, camera_height = Config().current_file()[
            'maps'][map_name]['camera']
        if self._y % camera_height == 0 or self._x % camera_width == 0:
            erase_line = ''
            if self._x % camera_width != 0:
                erase_line = 'border-left: none;'
            if self._y % camera_height != 0:
                erase_line = 'border-top: none;'
            self.setStyleSheet(
                'QWidget {'
                'border: 1px solid black;'
                'border-right: none;'
                'border-bottom: none;'
                '%s'
                '}' % erase_line)

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap
        self.setPixmap(self._pixmap.scaled(self.width(), self.height()))

    def clear_pixmap(self):
        self._pixmap = None
        self.setPixmap(QtGui.QPixmap(os.path.join(
            settings.IMAGES_PATH, 'blank.png'
        )))

    def x(self):
        return self._x

    def y(self):
        return self._y

    def update_size(self, x, y, width, height):
        self.setGeometry(x, y, width, height)
        if self._pixmap:
            self.setPixmap(self._pixmap.scaled(width, height))
        if self._special:
            self._special.setGeometry(0, 0, width, height)
            self._special.setPixmap(self._special.pixmap().scaled(
                width, height
            ))

    def pixmap(self):
        return self._pixmap
