# -*- coding: utf-8 *-*

import os
from PyQt4 import QtGui
from PyQt4 import QtCore

import settings

from mqme.config import Config
from mqme.mapgridlayer import MapGridLayer


class MapSpecialsLayer(MapGridLayer):

    NAME = 'Specials'

    TOOLS = [
        ('start_pos', 'Set the start position'),
        ('monster', 'Add monster'),
    ]

    def __init__(self, parent, map_obj):
        super(MapSpecialsLayer, self).__init__(parent, map_obj)
        self._current_special = None
        if not 'specials' in self._map_conf:
            self._map_conf['specials'] = []
            for x in range(map_obj['width']):
                matrix_line = []
                for y in range(map_obj['height']):
                    matrix_line.append({'class_name': None})
                self._map_conf['specials'].append(matrix_line)

    def set_current_tool(self, tool):
        super(MapSpecialsLayer, self).set_current_tool(tool)
        for tool in self.TOOLS:
            class_name, label = tool
            if class_name == self._current_tool:
                self._current_special = class_name

    def on_mouse_down(self, event, item):
        if self._current_special and event.button() == QtCore.Qt.LeftButton:
            callback = getattr(self, 'on_set_%s' % self._current_special)
            if callback(event, item) is not False:
                item.set_pixmap(QtGui.QPixmap(os.path.join(
                    settings.IMAGES_PATH,
                    self._current_special + '.png'
                )))
        elif event.button() == QtCore.Qt.RightButton:
            item.clear_pixmap()
            self._map_conf['specials'][item.x()][item.y()] = {
                'class_name': None
            }

    def on_mouse_move(self, event, item):
        pass

    def on_mouse_up(self, event, item):
        pass

    def on_set_monster(self, event, item):
        name, status = QtGui.QInputDialog.getText(
            self, 'Animation name', 'Name :'
        )
        if status:
            name = str(name)
            self._map_conf['specials'][item.x()][item.y()] = {
                'class_name': self._current_special,
                'monster_name': name
            }
        else:
            return False

    def on_set_start_pos(self, event, item):
        x = 0
        for matrix_line in self._map_conf['specials']:
            y = 0
            for special_conf in matrix_line:
                if special_conf['class_name'] == 'start_pos':
                    special_conf['class_name'] = None
                    self._items[x][y].clear_pixmap()
                y += 1
            x += 1

        self._map_conf['specials'][item.x()][item.y()] = {
            'class_name': self._current_special
        }

    def read_map_conf(self):
        self._map_conf = Config().current_file()[
            'maps'][self._map_obj['name']]
        x = 0
        for matrix_line in self._map_conf['specials']:
            y = 0
            for special_conf in matrix_line:
                if special_conf['class_name'] is not None:
                    self._items[x][y].set_pixmap(QtGui.QPixmap(os.path.join(
                        settings.IMAGES_PATH,
                        special_conf['class_name'] + '.png'
                    )))
                y += 1
            x += 1
