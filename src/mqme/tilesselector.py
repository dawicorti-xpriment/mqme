# -*- coding: utf-8 *-*
from PyQt4 import QtGui

from mqme.config import Config
from mqme.selectabletile import SelectableTile


class TilesSelector(QtGui.QFrame):

    def __init__(self, parent, callback, name):
        super(TilesSelector, self).__init__(parent)
        self._name = name
        self.current_file = Config().current_file()
        self._tiles = []
        self.setStyleSheet('QFrame {'
            'border: 1px solid black;'
            'background-color: white;'
            'border-radius: 5px;'
        '}')
        self._callback = callback

    def unselect_all(self):
        for tile in self._tiles:
            tile.setStyleSheet('QWidget {border: none;}')

    def on_select_tile(self, tile):
        self._callback(tile)
        tile.setStyleSheet('QWidget {border: 5px solid blue;}')

    def update(self):
        for tile in self._tiles:
            tile.hide()
        self._tiles = []
        row = 0
        col = 0
        for tile_name in self.current_file['tilesets'][self._name].keys():
            tile = SelectableTile(
                self, self.on_select_tile, self._name, tile_name
            )
            tile.setGeometry(col * 60, row * 60, 50, 50)
            tile.show()
            self._tiles.append(tile)
            col += 1
            if col == 2:
                col = 0
                row += 1
