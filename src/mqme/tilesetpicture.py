# -*- coding: utf-8 *-*
import os
from PyQt4 import QtGui

from mqme.tileitem import TileItem
from mqme.config import Config


class TileSetPicture(QtGui.QLabel):

    def __init__(self, parent, picture_path, queue):
        super(TileSetPicture, self).__init__(parent)
        self._parent = parent
        self._queue = queue
        self._items = []
        self._base_pixmap = QtGui.QPixmap(picture_path)
        self.config = Config()
        self.current_file = self.config.current_file()
        path_elements = os.path.split(picture_path)
        self._base_name = os.path.splitext(
            path_elements[len(path_elements) - 1]
        )[0]
        if not 'tilesets' in self.current_file:
            self.current_file['tilesets'] = {}
        if not 'pathes' in self.current_file:
            self.current_file['pathes'] = {}
        self.current_file['pathes'][self._base_name] = picture_path
        if not self._base_name in self.current_file['tilesets']:
            self.current_file['tilesets'][self._base_name] = {}
        self._current_item = None

    def base_name(self):
        return self._base_name

    def pixmap(self):
        return self._base_pixmap

    def read_tilesets_config(self):
        self.current_file = self.config.current_file()
        tileset_dict = self.current_file['tilesets'][self._base_name]
        for tile_name, tile in tileset_dict.items():
            item = TileItem(self, self._queue,
                tile['crop_x'], tile['crop_y'],
                tile['crop_width'], tile['crop_height']
            )
            item.set_name(tile_name)
            item.show()
            self._items.append(item)

    def set_height(self, height):
        pixmap = self._base_pixmap.scaledToHeight(height)
        self.setGeometry(0, 0, pixmap.width(), pixmap.height())
        self.setPixmap(pixmap)
        for item in self._items:
            item.update_geometry()

    def mousePressEvent(self, event):
        self._current_item = TileItem(self, self._queue, event.x(), event.y())
        self._current_item.show()

    def mouseReleaseEvent(self, event):
        if self._current_item is not None:
            if self._current_item.real_width() == 1:
                self._current_item.hide()
            else:
                status = False
                while not status:
                    name, status = QtGui.QInputDialog.getText(
                        self._parent, 'Tile name', 'Name :'
                    )
                name = str(name)
                self._current_item.set_name(name)
                self.current_file['tilesets'][
                    self._base_name
                ][name] = self._current_item.to_dict()
                self.current_file['tilesets']
                self._items.append(self._current_item)
                self._queue.put({'name': 'config.save'})
                self._queue.put({
                    'name': 'tileset.update',
                    'tileset': self._base_name
                })
            self._current_item = None

    def mouseMoveEvent(self, event):
        if self._current_item is not None:
            rect = self._current_item.geometry()
            width = event.x() - rect.x()
            if width < 3:
                width = 3
            height = event.y() - rect.y()
            if height < 3:
                height = 3
            self._current_item.set_size(width, height)

    def remove_item(self, item):
        self._items.pop(self._items.index(item))
        item.hide()
        del self.current_file[
            'tilesets'
        ][self._base_name][item.to_dict()['name']]

    def remove(self):
        del self.current_file['tilesets'][self._base_name]
