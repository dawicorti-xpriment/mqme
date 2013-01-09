# -*- coding: utf-8 *-*
from PyQt4 import QtGui
from mqme.mapgriditem import MapGridItem
from mqme.config import Config


class MapGridLayer(QtGui.QWidget):

    def __init__(self, parent, map_obj):
        super(MapGridLayer, self).__init__(parent)
        self.setStyleSheet('MapGridLayer {background: #ff0000;}')
        self._map_obj = map_obj
        self._parent = parent
        self.show()
        self._items = []
        self.config = Config()
        self._current_file = Config().current_file()
        self._map_conf = self._current_file['maps'][self._map_obj['name']]
        for x in range(map_obj['width']):
            items_line = []
            for y in range(map_obj['height']):
                items_line.append(MapGridItem(
                    self, self._map_obj['name'], x, y
                ))
            self._items.append(items_line)
        self._current_tool = None
        self._filled_items = []
        self._pixmap_input_filler = None

    def set_current_tool(self, tool):
        self._current_tool = tool

    def update_size(self):
        self.setGeometry(0, 0, self._parent.width(), self._parent.height())
        square_size = self.width() / self._map_obj['width']
        for x in range(self._map_obj['width']):
            for y in range(self._map_obj['height']):
                self._items[x][y].update_size(
                    x * square_size, y * square_size, square_size, square_size
                )

    def _get_item(self, event):
        for x in range(self._map_obj['width']):
            for y in range(self._map_obj['height']):
                if self._items[x][y].geometry().contains(event.x(), event.y()):
                    return self._items[x][y]

    def mousePressEvent(self, event):
        self.on_mouse_down(event, self._get_item(event))

    def mouseMoveEvent(self, event):
        self.on_mouse_move(event, self._get_item(event))

    def mouseReleaseEvent(self, event):
        self.on_mouse_up(event, self._get_item(event))
