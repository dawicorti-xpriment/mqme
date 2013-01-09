# -*- coding: utf-8 *-*
import os
from PyQt4 import QtGui


from mqme.childwindow import ChildWindow
from mqme.tilesetworkspace import TileSetWorkspace
from mqme.config import Config


class TilesEditor(ChildWindow):

    def __init__(self):
        super(TilesEditor, self).__init__()
        self.config = Config()
        self.setWindowTitle('Tiles Editor')
        self.setFixedSize(640, 480)
        self._tab_widget = QtGui.QTabWidget(self)
        self._tab_widget.setGeometry(0, 0, 640, 480)
        self.subscribe('menu.trigger.import_tileset', self.on_import_tileset)
        self.subscribe('picture.mousemove', self.on_picture_mouse_move)
        self.subscribe('new_project', self.on_new_file)
        self.subscribe('open_project', self.on_open_file)
        self._workspaces = []

    def on_new_file(self, message):
        self._workspaces = []
        self._tab_widget.clear()

    def on_open_file(self, message):
        self.current_file = self.config.current_file()
        for tileset in self.current_file.get('tilesets', []):
            workspace = TileSetWorkspace(
                self, self.current_file['pathes'][tileset], self._queue
            )
            workspace.show()
            self._tab_widget.addTab(workspace, workspace.base_name())
            self._workspaces.append(workspace)
            self.send('tileset_editor.new_tileset', {
                'tileset': workspace.base_name()
            })
            self.send('tileset.update', {
                'tileset': workspace.base_name()
            })
            workspace.read_tilesets_config()
        self.send('open_maps')

    def on_import_tileset(self, message):
        file_name = QtGui.QFileDialog.getOpenFileName(
            self, filter='Tilesets (*.png)',
            directory=self.config.get(
                'tilesets_images_dir', os.path.expanduser('~')
            )
        )
        if file_name:
            self.config.set(
                'tilesets_images_dir',
                os.path.dirname(str(file_name))
            )
            self.send('config.save')
            workspace = TileSetWorkspace(
                self, str(file_name), self._queue
            )
            workspace.show()
            self._tab_widget.addTab(workspace, workspace.base_name())
            self._workspaces.append(workspace)
            self.send('tileset_editor.new_tileset', {
                'tileset': workspace.base_name()
            })

    def on_picture_mouse_move(self, message):
        for workspace in self._workspaces:
            workspace.on_picture_mouse_move(message)

    def remove_current(self):
        self._workspaces.pop(self._tab_widget.currentIndex())
        self._tab_widget.removeTab(self._tab_widget.currentIndex())
