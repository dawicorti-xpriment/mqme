# -*- coding: utf-8 *-*
from PyQt4 import QtGui

from mqme.childwindow import ChildWindow
from mqme.mapeditor import MapEditor


class LayersDialog(ChildWindow):

    def __init__(self):
        super(LayersDialog, self).__init__()
        self.setFixedSize(300, len(MapEditor.LAYERS) * 100)
        self.setWindowTitle('Map layers')
        index = 0
        self._checkboxes = {}
        for layer_type in MapEditor.LAYERS:
            checkbox = QtGui.QCheckBox(layer_type.NAME, self)
            checkbox.setGeometry(0, index * 100, 300, 100)
            if index == 0:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_state_changed)
            self._checkboxes[checkbox] = layer_type
            index += 1

    def on_state_changed(self, state):
        for checkbox, layer_type in self._checkboxes.items():
            action = {
                True: 'show', False: 'hide'
            }[checkbox.isChecked()]
            self.send('%s_map_layer' % action, {'layer_type': layer_type})
