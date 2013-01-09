# -*- coding: utf-8 *-*
from PyQt4 import QtGui

from mqme.config import Config


class SelectableTile(QtGui.QLabel):

    def __init__(self, parent, callback, tileset, tile):
        super(SelectableTile, self).__init__(parent)
        self.config = Config()
        self.current_file = Config().current_file()
        tile_infos = self.current_file['tilesets'][tileset][tile]
        self.setPixmap(
            QtGui.QPixmap(self.current_file['pathes'][tileset]).copy(
                tile_infos['crop_x'], tile_infos['crop_y'],
                tile_infos['crop_width'], tile_infos['crop_height']
            ).scaled(50, 50)
        )
        self.config.set_cache('tiles/%s/%s' % (tileset, tile), self.pixmap())
        self._callback = callback
        self._tileset = tileset
        self._tile = tile

    def tile(self):
        return self._tile

    def tileset(self):
        return self._tileset

    def mousePressEvent(self, event):
        self._callback(self)
