# -*- coding: utf-8 *-*
from PyQt4 import QtCore

from mqme.mapgridlayer import MapGridLayer
from mqme.selectabletile import SelectableTile


class MapForegroundLayer(MapGridLayer):

    NAME = 'Foreground Tiles'

    def __init__(self, parent, map_obj):
        super(MapForegroundLayer, self).__init__(parent, map_obj)
        self._current_tile = None
        if not 'foreground' in self._map_conf:
            self._map_conf['foreground'] = []
            for x in range(map_obj['width']):
                matrix_line = []
                for y in range(map_obj['height']):
                    matrix_line.append({'name': None, 'path': None})
                self._map_conf['foreground'].append(matrix_line)

    def set_current_tool(self, tool):
        if type(tool) == SelectableTile:
            self._current_tile = tool
        else:
            self._current_tile = None
        super(MapForegroundLayer, self).set_current_tool(tool)

    def on_mouse_down(self, event, item):
        if self._current_tile:
            if event.button() == QtCore.Qt.LeftButton:
                item.set_pixmap(self._current_tile.pixmap())
                self._map_conf['foreground'][item.x()][item.y()] = {
                    'name': self._current_tile.tile(),
                    'path': 'tiles/%s' % self._current_tile.tileset()
                }
                self._filled_items.append(item)
                self._slide_activated = True
        elif event.button() == QtCore.Qt.RightButton:
            item.clear_pixmap()
            self._map_conf['foreground'][item.x()][item.y()] = {
                'name': None,
                'path': None
            }

    def on_mouse_up(self, event, item):
        self._filled_items = []

    def on_mouse_move(self, event, item):
        if self._current_tile and self._filled_items \
                and not item in self._filled_items:
            item.set_pixmap(self._current_tile.pixmap())
            self._map_conf['foreground'][item.x()][item.y()] = {
                'name': self._current_tile.tile(),
                'path': 'tiles/%s' % self._current_tile.tileset()
            }
            self._filled_items.append(item)

    def read_map_conf(self):
        map_conf = self._current_file['maps'][self._map_obj['name']]
        x = 0
        y = 0
        for x_line in map_conf.get('foreground', []):
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
