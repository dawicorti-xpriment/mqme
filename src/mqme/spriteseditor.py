# -*- coding: utf-8 *-*
from PyQt4 import QtGui

from mqme.childwindow import ChildWindow
from mqme.actorworkspace import ActorWorkspace
from mqme.config import Config


class SpritesEditor(ChildWindow):

    def __init__(self):
        super(SpritesEditor, self).__init__()
        self.setFixedSize(640, 480)
        self.setWindowTitle('Sprites Editor')
        self._tabs_widget = QtGui.QTabWidget(self)
        self._tabs_widget.setGeometry(0, 0, 640, 480)
        self._tabs_widget.setTabsClosable(True)
        self._tabs_widget.tabCloseRequested.connect(self.on_actor_delete)
        self._current_file = Config().current_file()
        self.subscribe('menu.trigger.new_actor', self.on_new_actor)
        self.subscribe('open_project', self.on_open_file)
        self.subscribe('new_project', self.on_new_file)

    def on_actor_delete(self, index):
        actor_name = self._tabs_widget.widget(index).actor_name()
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle('Delete Actor')
        msg_box.setText('Do you want to delete "%s" ?' % actor_name)
        msg_box.setStandardButtons(
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
        )
        msg_box.setDefaultButton(QtGui.QMessageBox.Cancel)
        status = msg_box.exec_()
        if status == QtGui.QMessageBox.Ok:
            self._tabs_widget.widget(index).remove_actor()
            self._tabs_widget.removeTab(index)

    def on_new_actor(self, message):
        name, status = QtGui.QInputDialog.getText(
            self, 'Actor name', 'Name :'
        )
        if status:
            name = str(name)
            if not 'actors' in self._current_file:
                self._current_file['actors'] = {}
            self._current_file['actors'][name] = {}
            self._tabs_widget.addTab(ActorWorkspace(name), name)

    def on_new_file(self, message):
        self._tabs_widget.clear()

    def on_open_file(self, message):
        self._current_file = Config().current_file()
        for name in self._current_file.get('actors', {}):
            workspace = ActorWorkspace(name)
            workspace.read_conf()
            self._tabs_widget.addTab(workspace, name)
