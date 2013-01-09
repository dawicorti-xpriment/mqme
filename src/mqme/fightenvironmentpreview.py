from PyQt4 import QtGui
from PyQt4 import QtCore

import settings

from mqme.config import Config


class FightEnvironmentPreview(QtGui.QDialog):

    LAYERS = ('background3', 'background2', 'background1')

    SCROLL_GAP = int(settings.FIGHTENV_SCROLL_GAP * 300)

    def __init__(self, environment_name):
        super(FightEnvironmentPreview, self).__init__()
        self._environment_name = environment_name
        self.current_conf = Config().current_file()[
            'fightenv'
        ][environment_name]
        self._height_ratio = 1.0
        self.setStyleSheet('QDialog {background-color: black;}')
        self.setModal(True)
        self.setWindowTitle(environment_name)
        self.setFixedSize(300, 150)
        self._layers = {}
        self._layer_period_buffer = {}
        for base_layer_name in self.LAYERS:
            self._layer_period_buffer[base_layer_name] = 0
            for index in range(2):
                layer_name = '%s_%d' % (base_layer_name, index)
                self._layers[layer_name] = self.new_layer()
                if base_layer_name in self.current_conf:
                    layer = self._layers[layer_name]
                    pixmap = QtGui.QPixmap(
                        Config().current_file()['pathes'][
                            self.current_conf[base_layer_name]
                        ]
                    )
                    self.show_background(pixmap, base_layer_name, index)
                    rect = layer.geometry()
                    if index == 0:
                        layer.setGeometry(
                            0, rect.y(), rect.width(), rect.height()
                        )
                    else:
                        previous_layer_name = '%s_%d' % (
                            base_layer_name, index - 1
                        )
                        previous_layer = self._layers[previous_layer_name]
                        layer.setGeometry(
                            previous_layer.x() + previous_layer.width(),
                            rect.y(), rect.width(), rect.height()
                        )
        self._timer = QtCore.QTimer()
        self._timer.setInterval(25)
        self._timer.timeout.connect(self._on_timeout)
        self._timer.start()

    def _on_timeout(self):
        for base_layer_name in self.LAYERS:
            self._layer_period_buffer[base_layer_name] += 25
            if self._layer_period_buffer[base_layer_name] \
                    >= settings.FIGHTENV_SCROLL_PERIODS[base_layer_name]:
                self._layer_period_buffer[base_layer_name] = 0
                for index in range(2):
                    layer_name = '%s_%d' % (base_layer_name, index)
                    layer = self._layers[layer_name]
                    rect = QtCore.QRect(layer.geometry())
                    layer.setGeometry(
                        rect.x() - self.SCROLL_GAP, rect.y(),
                        rect.width(), rect.height()
                    )
                for index in range(2):
                    layer_name = '%s_%d' % (base_layer_name, index)
                    layer = self._layers[layer_name]
                    rect = QtCore.QRect(layer.geometry())
                    if rect.x() + rect.width() <= 0:
                        previous_index = index - 1
                        if previous_index < 0:
                            previous_index = 1
                        previous_layer_name = '%s_%d' % (
                            base_layer_name, previous_index
                        )
                        previous_layer = self._layers[previous_layer_name]
                        layer.setGeometry(
                            previous_layer.geometry().right(),
                            rect.y(), rect.width(), rect.height()
                        )

    def closeEvent(self, event):
        self._timer.stop()

    def show_background(self, pixmap, base_layer_name, index):
        layer_name = '%s_%d' % (base_layer_name, index)
        layer = self._layers[layer_name]
        height = self.height()
        self._height_ratio = float(height) / pixmap.height()
        width = (pixmap.width() * height) / pixmap.height()
        pixmap = pixmap.scaled(width, height)
        rect = QtCore.QRect(self._layers[layer_name].geometry())
        rect.setWidth(pixmap.width())
        layer.setGeometry(rect)
        layer.setPixmap(pixmap)

    def new_layer(self):
        layer = QtGui.QLabel(self)
        layer.setGeometry(0, 0, self.width(), self.height())
        layer.show()
        return layer
