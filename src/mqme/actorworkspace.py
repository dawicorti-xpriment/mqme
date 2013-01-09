# -*- coding: utf-8 *-*
from PyQt4 import QtGui

from mqme.animationarea import AnimationArea
from mqme.config import Config


class ActorWorkspace(QtGui.QFrame):

    def __init__(self, name):
        super(ActorWorkspace, self).__init__()
        self._actor_name = name
        self._current_conf = Config().current_file()['actors'][name]
        self.setGeometry(0, 50, 640, 430)
        self._animations_list = QtGui.QListWidget(self)
        self._animations_list.setGeometry(485, 40, 150, 405)
        self._animations_list.itemClicked.connect(self.on_choose_animation)
        self._new_animation_button = QtGui.QPushButton('New animation', self)
        self._new_animation_button.setGeometry(485, 2, 150, 36)
        self._new_animation_button.clicked.connect(self.on_new_animation)
        self._animation_areas = {}

    def read_conf(self):
        for name in self._current_conf.get('animations', {}):
            self._animation_areas[name] = AnimationArea(
                self, self._actor_name, name
            )
            self._animation_areas[name].read_conf()
            self._animation_areas[name].hide()
            self._animations_list.addItem(name)

    def on_choose_animation(self, item):
        for name, area in self._animation_areas.items():
            if name == item.text():
                area.show()
            else:
                area.hide()

    def remove_animation(self, animation_name):
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle('Remove Animation')
        msg_box.setText(
            'Do you want to remove animation "%s" ?' % animation_name
        )
        msg_box.setStandardButtons(
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel
        )
        msg_box.setDefaultButton(QtGui.QMessageBox.Cancel)
        status = msg_box.exec_()
        if status == QtGui.QMessageBox.Ok:
            self._animation_areas[animation_name].remove_animation()
            for index in range(self._animations_list.count()):
                item = self._animations_list.item(index)
                if item.text() == animation_name:
                    self._animations_list.takeItem(index)
                    break
            item = self._animations_list.item(0)
            self._animations_list.setCurrentItem(item)
            self._animation_areas[str(item.text())].show()
            del self._animation_areas[animation_name]

    def remove_actor(self):
        actors = Config().current_file()['actors']
        del actors[self._actor_name]

    def actor_name(self):
        return self._actor_name

    def on_new_animation(self):
        name, status = QtGui.QInputDialog.getText(
            self, 'Animation name', 'Name :'
        )
        if status:
            name = str(name)
            if not 'animations' in self._current_conf:
                self._current_conf['animations'] = {}
            self._current_conf['animations'][name] = {}
            self._animations_list.addItem(name)
            self._animation_areas[name] = AnimationArea(
                self, self._actor_name, name
            )
            self._animation_areas[name].show()
