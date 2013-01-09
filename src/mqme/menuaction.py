# -*- coding: utf-8 *-*
from PyQt4 import QtGui


class MenuAction(QtGui.QAction):

    def __init__(self, parent, name, callback):
        super(MenuAction, self).__init__(parent)
        self._name = name.lower().replace(' ...', '').replace(' ', '_')
        self._callback = callback
        self.setText(name)
        self.triggered.connect(self.on_action_triggered)

    def on_action_triggered(self):
        self._callback(self._name)
