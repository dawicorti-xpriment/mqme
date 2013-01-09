# -*- coding: utf-8 *-*
import os
from PyQt4 import QtGui

import settings

from mqme.childwindow import ChildWindow
from mqme.config import Config
from mqme.newmapdialog import NewMapDialog
from mqme.mapgrid import MapGrid
from mqme.menuaction import MenuAction
from mqme.iconbutton import IconButton
from mqme.tilesselector import TilesSelector
from mqme.mapbackgroundlayer import MapBackgroundLayer
from mqme.mapblockmatrixlayer import MapBlockMatrixLayer
from mqme.mapforegroundlayer import MapForegroundLayer
from mqme.mapspecialslayer import MapSpecialsLayer


class MapEditor(ChildWindow):

    LAYERS = [
        MapBackgroundLayer,
        MapBlockMatrixLayer,
        MapForegroundLayer,
        MapSpecialsLayer
    ]

    def __init__(self):
        super(MapEditor, self).__init__()
        self.config = Config()
        self.setFixedSize(900, 600)
        self.setWindowTitle('Map Editor')
        self.subscribe('menu.trigger.new_map', self.on_new_map)
        self.subscribe('tileset_editor.new_tileset', self.on_new_tileset)
        self.subscribe('tileset.update', self.on_tileset_update)
        self.subscribe('open_maps', self.on_open_maps)
        self.subscribe('hide_map_layer', self.on_hide_layer)
        self.subscribe('show_map_layer', self.on_show_layer)
        self._toolbox = QtGui.QToolBar(self)
        self._toolbox.setGeometry(0, 0, 100, 600)
        self._actions = {}
        for tool in MapSpecialsLayer.TOOLS:
            ref, name = tool
            action = MenuAction(self._toolbox, ref, self.on_action_checked)
            action.setIcon(QtGui.QIcon(os.path.join(
                settings.IMAGES_PATH, '%s.png' % ref
            )))
            action.setText(name)
            action.setCheckable(True)
            self._toolbox.addAction(action)
            self._actions[ref] = action
        self._tab_widget = QtGui.QTabWidget(self)
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.tabCloseRequested.connect(self.on_map_delete)
        self._tab_widget.setGeometry(100, 0, 550, 550)
        self._zoom_in = IconButton(self, 'zoom_in', 30, 30)
        self._zoom_in.setGeometry(150, 560, 30, 30)
        self._zoom_in.clicked.connect(self.on_zoom_in)
        self._zoom_out = IconButton(self, 'zoom_out', 30, 30)
        self._zoom_out.setGeometry(110, 560, 30, 30)
        self._zoom_out.clicked.connect(self.on_zoom_out)
        self._tileset_cb = QtGui.QComboBox(self)
        self._tileset_cb.setGeometry(665, 5, 220, 20)
        self._tileset_cb.currentIndexChanged.connect(self.update)
        self._tiles_widgets = {}
        self._current_tool = None

    def on_map_delete(self, index):
        map_name = self._tab_widget.widget(index).map_name()
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle('Delete Map')
        msg_box.setText('Do you want to delete "%s" ?' % map_name)
        msg_box.setStandardButtons(
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
        )
        msg_box.setDefaultButton(QtGui.QMessageBox.Cancel)
        status = msg_box.exec_()
        if status == QtGui.QMessageBox.Ok:
            self._tab_widget.widget(index).remove_map()
            self._tab_widget.removeTab(index)

    def on_hide_layer(self, message):
        index = 0
        while index < self._tab_widget.count():
            self._tab_widget.widget(index).hide_layer(message['layer_type'])
            index += 1

    def on_show_layer(self, message):
        index = 0
        while index < self._tab_widget.count():
            self._tab_widget.widget(index).show_layer(message['layer_type'])
            index += 1

    def on_action_checked(self, action_ref):
        for ref, action in self._actions.items():
            if ref != action_ref:
                action.setChecked(False)
        if self._actions[action_ref].isChecked():
            self._current_tool = action_ref
        else:
            self._current_tool = None
        self._tab_widget.currentWidget().set_current_tool(self._current_tool)

    def on_open_maps(self, message):
        current_file = self.config.current_file()
        for map_name, map_obj in current_file.get('maps', {}).items():
            map_grid = MapGrid(self, map_obj, self.LAYERS)
            map_grid.read_map_conf()
            map_grid.show_layer(MapBackgroundLayer)
            self._tab_widget.addTab(map_grid, map_name)

    def on_new_project(self, message):
        self._current_tool = None
        for widget in self._tiles_widgets.values():
            widget.hide()
        self._tileset_cb.clear()
        self._tiles_widgets = {}
        self._tab_widget.clear()

    def on_select_tile(self, tile):
        for selector in self._tiles_widgets.values():
            selector.unselect_all()
        self._current_tool = tile
        self._tab_widget.currentWidget().set_current_tool(tile)

    def on_new_tileset(self, message):
        self._tileset_cb.addItem(message['tileset'])
        self._tiles_widgets[message['tileset']] = TilesSelector(
            self, self.on_select_tile, message['tileset']
        )
        self._tiles_widgets[message['tileset']].setGeometry(665, 30, 220, 560)
        self.update()

    def update(self, index=None):
        for name in self._tiles_widgets.keys():
            self._tiles_widgets[name].hide()
        current_tileset = str(self._tileset_cb.currentText())
        if current_tileset in self._tiles_widgets:
            self._tiles_widgets[current_tileset].show()

    def on_tileset_update(self, message):
        if message['tileset'] in self._tiles_widgets:
            self._tiles_widgets[message['tileset']].update()

    def on_new_map(self, message):
        map_obj = NewMapDialog.get_new_map(self)
        if map_obj is not None:
            self._tab_widget.addTab(MapGrid(
                self, map_obj, self.LAYERS), map_obj['name']
            )

    def on_zoom_in(self):
        self._tab_widget.currentWidget().on_zoom_in()

    def on_zoom_out(self):
        self._tab_widget.currentWidget().on_zoom_out()
