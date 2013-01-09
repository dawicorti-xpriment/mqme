# -*- coding: utf-8 *-*
from PyQt4 import QtGui

from mqme.config import Config
from mqme.iconbutton import IconButton
from mqme.tilesetpicture import TileSetPicture


class TileSetWorkspace(QtGui.QWidget):

    ZOOM_VALUES = [1, 2, 2.5, 3, 4, 5, 8, 10]

    def __init__(self, parent, picture_path, queue):
        super(TileSetWorkspace, self).__init__(parent)
        self._parent = parent
        self.setGeometry(0, 48, 640, 432)
        self.config = Config()
        self._queue = queue
        rect = self.geometry()
        self._pos_label = QtGui.QLabel(self)
        self._pos_label.setGeometry(
            rect.right() - 100, rect.top() + 130, 100, 100
        )
        self._delete = IconButton(self, 'delete_tileset', 20, 20)
        self._delete.clicked.connect(self.remove)
        self._delete.setGeometry(rect.right() - 25, rect.top() + 5, 20, 20)
        self._zoom_in = IconButton(self, 'zoom_in', 50, 50)
        self._zoom_in.clicked.connect(self.on_zoom_in)
        self._zoom_in.setGeometry(rect.right() - 55, rect.top() + 35, 50, 50)
        self._zoom_out = IconButton(self, 'zoom_out', 50, 50)
        self._zoom_out.clicked.connect(self.on_zoom_out)
        self._zoom_out.setGeometry(rect.right() - 55, rect.top() + 90, 50, 50)
        self._scroll_area = QtGui.QScrollArea(self)
        self._scroll_area.setGeometry(
            2, 2, rect.width() - 104, rect.height() - 4
        )
        self._scroll_area.setStyleSheet('QScrollArea {'
            'background: black;'
            'border: 3px solid #ccccff;'
        '}')
        self._tileset_picture = TileSetPicture(
            self, picture_path, self._queue
        )
        self._scroll_area.setWidget(self._tileset_picture)
        self._zoom_index = 0
        self.update_zoom()

    def read_tilesets_config(self):
        self._tileset_picture.read_tilesets_config()

    def base_name(self):
        return self._tileset_picture.base_name()

    def update_zoom(self):
        self._tileset_picture.set_height(
            self.ZOOM_VALUES[self._zoom_index] * 400
        )

    def on_zoom_in(self):
        if self._zoom_index + 1 < len(self.ZOOM_VALUES):
            self._zoom_index += 1
        self.update_zoom()

    def on_zoom_out(self):
        if self._zoom_index - 1 >= 0:
            self._zoom_index -= 1
        self.update_zoom()

    def on_picture_mouse_move(self, message):
        self._pos_label.setText('X : %d\nY : %d\nWidth : %d\nHeight : %d' % (
            message['x'], message['y'], message['width'], message['height']
        ))

    def remove(self):
        self._tileset_picture.remove()
        self._parent.remove_current()
