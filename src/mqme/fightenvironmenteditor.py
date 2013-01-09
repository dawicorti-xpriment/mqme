from PyQt4 import QtGui

from mqme.childwindow import ChildWindow
from mqme.config import Config
from mqme.fightenvironmentworkspace import FightEnvironmentWorkspace


class FightEnvironmentEditor(ChildWindow):

    def __init__(self):
        super(FightEnvironmentEditor, self).__init__()
        self.setWindowTitle('Fight Environment Editor')
        self.setFixedSize(320, 240)
        self._tabs_widget = QtGui.QTabWidget(self)
        self._tabs_widget.setGeometry(0, 0, 320, 240)
        self._tabs_widget.setTabsClosable(True)
        self._tabs_widget.tabCloseRequested.connect(self.on_environment_delete)
        self.subscribe(
            'menu.trigger.new_fight_environment', self.on_new_environment
        )
        self._current_file = Config().current_file()
        self.subscribe('open_project', self.on_open_file)

    def on_open_file(self, message):
        self._current_file = Config().current_file()
        for name in self._current_file.get('fightenv', {}):
            workspace = FightEnvironmentWorkspace(name)
            workspace.read_conf()
            self._tabs_widget.addTab(workspace, name)

    def on_environment_delete(self, index):
        name = self._tabs_widget.widget(index).name()
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle('Delete Fight Environment')
        msg_box.setText('Do you want to delete "%s" ?' % name)
        msg_box.setStandardButtons(
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
        )
        msg_box.setDefaultButton(QtGui.QMessageBox.Cancel)
        status = msg_box.exec_()
        if status == QtGui.QMessageBox.Ok:
            del self._current_file['fightenv'][name]
            self._tabs_widget.removeTab(index)

    def on_new_environment(self, message):
        name, status = QtGui.QInputDialog.getText(
            self, 'Fight Environment name', 'Name :'
        )
        if status:
            name = str(name)
            if not 'fightenv' in self._current_file:
                self._current_file['fightenv'] = {}
            self._current_file['fightenv'][name] = {}
            self._tabs_widget.addTab(FightEnvironmentWorkspace(name), name)
