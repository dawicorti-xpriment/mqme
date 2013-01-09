# -*- coding: utf-8 *-*
import os
from PyQt4 import QtGui

import settings


class IconButton(QtGui.QPushButton):

    def __init__(self, parent, icon_name, width=None, height=None):
        super(IconButton, self).__init__(parent)
        base_pixmap = QtGui.QPixmap(os.path.join(
            settings.IMAGES_PATH, icon_name + '.png'
        ))
        if width is None:
            pixmap = base_pixmap.scaledToHeight(height)
        elif height is None:
            pixmap = base_pixmap.scaledToWidth(width)
        else:
            pixmap = base_pixmap.scaled(width, height)
        self.setIcon(QtGui.QIcon(pixmap))
        self._checkable = False
        self._checked = False
        self._check_action = QtGui.QAction("Checked", self)
        self.checked = self._check_action.triggered

    def set_checkable(self, checkable):
        self._checkable = checkable

    def mousePressEvent(self, event):
        if not self._checkable:
            return super(IconButton, self). mousePressEvent(event)
        if not self._checked:
            self.setStyleSheet('QWidget {background-color: #00dddd;}')
            self._checked = True
            self.checked.emit(True)
        else:
            self._checked = False
            self.checked.emit(False)
            self.setStyleSheet(
                'QWidget {background-color: none; background: none;}'
            )
