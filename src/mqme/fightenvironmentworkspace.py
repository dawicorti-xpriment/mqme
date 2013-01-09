import os
import uuid
from PyQt4 import QtGui

from mqme.iconbutton import IconButton
from mqme.fightenvironmentpreview import FightEnvironmentPreview
from mqme.config import Config


class FightEnvironmentWorkspace(QtGui.QFrame):

    LAYERS = ('screen', 'background3', 'background2', 'background1')

    def __init__(self, name):
        super(FightEnvironmentWorkspace, self).__init__()
        self._name = name
        self._height_ratio = 1.0
        self.config = Config()
        self.setGeometry(0, 0, 320, 220)
        self._layers = {}
        self._buttons = []
        self._current_conf = Config().current_file()['fightenv'][name]
        for layer_name in self.LAYERS:
            self._layers[layer_name] = self.new_layer()
        self._layers['screen'].setStyleSheet(
            'QLabel {'
            'background-color: black;'
            'border: 3px solid #ccccff;'
            '}'
        )
        self.new_button('Set background 1', 2, self.on_choose_background1, False)
        self.new_button('Set background 2', 104, self.on_choose_background2, False)
        self.new_button('Set background 3', 206, self.on_choose_background3)
        self._play_animation = IconButton(self, 'play_animation', 30, 30)
        self._play_animation.setGeometry(145, 182, 30, 30)
        self._play_animation.clicked.connect(self.on_play_animation)

    def on_play_animation(self):
        self._preview = FightEnvironmentPreview(self._name)
        self._preview.show()

    def name(self):
        return self._name

    def read_conf(self):
        for layer_name in self.LAYERS:
            if layer_name in self._current_conf:
                path = Config().current_file()['pathes'][self._current_conf[layer_name]]
                pixmap = QtGui.QPixmap(path)
                self.show_background(pixmap, layer_name)

    def show_background(self, pixmap, name):
        height = self._layers[name].height()
        width = (pixmap.width() * height) / pixmap.height()
        self._height_ratio = float(height) / pixmap.height()
        self._layers[name].setPixmap(pixmap.scaled(width, height))
        for button in self._buttons:
            button.setEnabled(True)

    def on_choose_background3(self):
        pixmap = self.choose_and_save_image('background3')
        if pixmap:
            self.show_background(pixmap, 'background3')

    def on_choose_background2(self):
        pixmap = self.choose_and_save_image('background2')
        if pixmap:
            self.show_background(pixmap, 'background2')

    def on_choose_background1(self):
        pixmap = self.choose_and_save_image('background1')
        if pixmap:
            self.show_background(pixmap, 'background1')

    def choose_and_save_image(self, image_name):
        file_name = QtGui.QFileDialog.getOpenFileName(
            self, filter='Image (*.png)',
            directory=self.config.get(
                'fightenv_image_dir', os.path.expanduser('~')
            )
        )
        if file_name:
            from mqme.mainwindow import MainWindow
            file_name = unicode(file_name)
            self.config.set('fightenv_image_dir', os.path.dirname(file_name))
            MainWindow.queue.put({'name': 'config.save'})
            if not 'pathes' in Config().current_file():
                Config().current_file()['pathes'] = {}
            image_id = str(uuid.uuid1())
            Config().current_file()['pathes'][image_id] = file_name
            self._current_conf[image_name] = image_id
            return QtGui.QPixmap(file_name)

    def new_button(self, name, x, callback, enabled=True):
        button = QtGui.QPushButton(name, self)
        button.setGeometry(x, 155, 100, 20)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        button.setStyleSheet(
            'QPushButton {'
            'font-size: 10px;'
            '}'
        )
        button.show()
        self._buttons.append(button)

    def new_layer(self):
        layer = QtGui.QLabel(self)
        layer.setGeometry(7, 0, 300, 150)
        layer.show()
        return layer
