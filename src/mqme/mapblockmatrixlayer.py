# -*- coding: utf-8 *-*
import os
from PyQt4 import QtGui

import settings

from mqme.mapgridlayer import MapGridLayer


class MapBlockMatrixLayer(MapGridLayer):

    NAME = 'Blocking Matrix'

    STATES = [
        'pass',
        'block',
        'up_block',
        'right_block',
        'down_block',
        'left_block',
    ]

    def __init__(self, parent, map_obj):
        super(MapBlockMatrixLayer, self).__init__(parent, map_obj)
        if not 'blocking' in self._map_conf:
            self._map_conf['blocking'] = []
            for x in range(map_obj['width']):
                matrix_line = []
                for y in range(map_obj['height']):
                    matrix_line.append(self.STATES.index('pass'))
                    self.update_item_symbol(self._items[x][y], 'pass')
                self._map_conf['blocking'].append(matrix_line)

    def update_item_symbol(self, item, value=None):
        if value is None:
            value = self.STATES[self._map_conf['blocking'][item.x()][item.y()]]
        item.set_pixmap(QtGui.QPixmap(
            os.path.join(settings.IMAGES_PATH, value + '.png')
        ))

    def on_mouse_down(self, event, item):
        self._map_conf['blocking'][item.x()][item.y()] += 1
        if self._map_conf['blocking'][item.x()][item.y()] == len(self.STATES):
            self._map_conf['blocking'][item.x()][item.y()] = 0
        self.update_item_symbol(item)

    def on_mouse_up(self, event, item):
        pass

    def on_mouse_move(self, event, item):
        pass

    def read_map_conf(self):
        for x in range(self._map_obj['width']):
            for y in range(self._map_obj['height']):
                self.update_item_symbol(self._items[x][y])
