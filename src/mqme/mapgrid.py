# -*- coding: utf-8 *-*
from PyQt4 import QtGui

from mqme.config import Config


class MapGrid(QtGui.QWidget):

    ZOOMS = [0.5, 0.6, 0.7, 0.8, 0.9, 1, 2, 3, 4]

    def __init__(self, parent, map_obj, layers_types):
        super(MapGrid, self).__init__(parent)
        self._map_obj = map_obj
        self._current_file = Config().current_file()
        if not 'maps' in self._current_file:
            self._current_file['maps'] = {}
        if not self._map_obj['name'] in self._current_file['maps']:
            self._current_file['maps'][self._map_obj['name']] = self._map_obj
        self._layers_widget = QtGui.QWidget(self)
        self._scroll_area = QtGui.QScrollArea(self)
        self._scroll_area.setWidget(self._layers_widget)
        self._scroll_area.setGeometry(0, 0, 550, 520)
        self._zoom_index = self.ZOOMS.index(1)
        self._layers = []
        for layer_type in layers_types:
            layer = layer_type(self._layers_widget, map_obj)
            layer.hide()
            self._layers.append(layer)
        self.update_grid_size()

    def remove_map(self):
        del Config().current_file()['maps'][self.map_name()]

    def map_name(self):
        return self._map_obj['name']

    def show_layer(self, layer_type):
        for layer in self._layers:
            if type(layer) == layer_type:
                layer.show()

    def hide_layer(self, layer_type):
        for layer in self._layers:
            if type(layer) == layer_type:
                layer.hide()

    def read_map_conf(self):
        for layer in self._layers:
            layer.read_map_conf()

    def set_current_tool(self, tool):
        for layer in self._layers:
            layer.set_current_tool(tool)

    def update_grid_size(self):
        width = self.ZOOMS[self._zoom_index] * self._map_obj['width'] * 32
        height = self.ZOOMS[self._zoom_index] * self._map_obj['height'] * 32
        self._layers_widget.setGeometry(
           (self._scroll_area.width() - width) / 2,
           (self._scroll_area.height() - height) / 2,
           width, height
        )
        for layer in self._layers:
            layer.update_size()

    def on_zoom_in(self):
        if self._zoom_index + 1 < len(self.ZOOMS) - 1:
            self._zoom_index += 1
            self.update_grid_size()

    def on_zoom_out(self):
        if self._zoom_index - 1 >= 0:
            self._zoom_index -= 1
            self.update_grid_size()
