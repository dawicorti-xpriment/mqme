# -*- coding: utf-8 *-*
from PyQt4 import QtCore

from mqme.mapgridlayer import MapGridLayer
from mqme.selectabletile import SelectableTile


class MapBackgroundLayer(MapGridLayer):

    NAME = 'Background Tiles'

    def __init__(self, parent, map_obj):
        super(MapBackgroundLayer, self).__init__(parent, map_obj)
        self._current_tile = None
        if not 'tiles' in self._map_conf:
            self._map_conf['tiles'] = []
            for x in range(map_obj['width']):
                matrix_line = []
                for y in range(map_obj['height']):
                    matrix_line.append({'name': '', 'path': ''})
                    if (x % 2 == 0 and y % 2 == 0) \
                            or (x % 2 != 0 and y % 2 != 0):
                        self._items[x][y].setStyleSheet(
                            'QWidget{background-color:black;}'
                        )
                    else:
                        self._items[x][y].setStyleSheet(
                            'QWidget{background-color:white;}'
                        )
                self._map_conf['tiles'].append(matrix_line)

    def set_current_tool(self, tool):
        if type(tool) == SelectableTile:
            self._current_tile = tool
        else:
            self._current_tile = None
        super(MapBackgroundLayer, self).set_current_tool(tool)

    def fill_from_item_index(self, x, y):
        try:
            self.fill_from_item(self._items[x][y])
        except IndexError:
            pass

    def fill_from_item(self, item):
        if item.pixmap() == self._pixmap_filler \
                and not item in self._filled_items:
            item.set_pixmap(self._current_tile.pixmap())
            self._map_conf['tiles'][item.x()][item.y()] = {
                'name': self._current_tile.tile(),
                'path': 'tiles/%s' % self._current_tile.tileset()
            }
            self._filled_items.append(item)
            self.fill_from_item_index(item.x(), item.y() - 1)
            self.fill_from_item_index(item.x(), item.y() + 1)
            self.fill_from_item_index(item.x() - 1, item.y())
            self.fill_from_item_index(item.x() + 1, item.y())

    def on_mouse_down(self, event, item):
        if self._current_tile:
            if event.button() == QtCore.Qt.LeftButton:
                item.set_pixmap(self._current_tile.pixmap())
                self._map_conf['tiles'][item.x()][item.y()] = {
                    'name': self._current_tile.tile(),
                    'path': 'tiles/%s' % self._current_tile.tileset()
                }
                self._filled_items.append(item)
                self._slide_activated = True
            elif event.button() == QtCore.Qt.RightButton:
                self._pixmap_filler = item.pixmap()
                self.fill_from_item(item)

    def on_mouse_up(self, event, item):
        self._filled_items = []

    def on_mouse_move(self, event, item):
        if self._current_tile and self._filled_items \
                and not item in self._filled_items:
            item.set_pixmap(self._current_tile.pixmap())
            self._map_conf['tiles'][item.x()][item.y()] = {
                'name': self._current_tile.tile(),
                'path': 'tiles/%s' % self._current_tile.tileset()
            }
            self._filled_items.append(item)

    def read_map_conf(self):
        map_conf = self._current_file['maps'][self._map_obj['name']]
        x = 0
        y = 0
        for x_line in map_conf.get('tiles', []):
            y = 0
            for tile in x_line:
                try:
                    self._items[x][y].set_pixmap(self.config.get_cache(
                        '%s/%s' % (tile['path'], tile['name'])
                    ))
                except KeyError:
                    pass
                y += 1
            x += 1
