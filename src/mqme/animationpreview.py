import os
from PyQt4 import QtGui
from PyQt4 import QtCore

import settings

from mqme.spritesgenerator import SpritesGenerator


class AnimationPreview(QtGui.QDialog):

    def __init__(self, parent, actor, animation):
        super(AnimationPreview, self).__init__(parent)
        self._counter = 0
        self.setModal(True)
        self.setFixedSize((5 * 32) + 20, (5 * 32) + 20)
        self._animation = animation
        self._generator = SpritesGenerator(actor)
        self.conf = self._generator.current_conf[
            'animations'][animation]
        n_frame = len(
            self._generator.current_conf['animations'][animation]
        ) - 1
        self._frames_pixmaps = []
        for frame_index in range(n_frame):
            image = self._generator.get_frame_as_image(
                animation, frame_index
            )
            path = os.path.join(
                settings.TMP_PATH, 'preview_frame_%d.png' % frame_index
            )
            image.save(path)
            self._frames_pixmaps.append(QtGui.QPixmap(path))
        self._current_frame = 0
        self._screen = QtGui.QFrame(self)
        self._screen.setGeometry(10, 10, 5 * 32, 5 * 32)
        self._screen.setStyleSheet('QFrame {background-color: black;}')
        self._picture = QtGui.QLabel(self._screen)
        self._picture.show()
        self._timer = QtCore.QTimer()
        self._timer.setInterval(
            1000 / self._generator.current_conf['animations'][animation]['fps']
        )
        self._timer.timeout.connect(self._on_timeout)
        self._timer.start()

    def _on_timeout(self):
        pixmap = self._frames_pixmaps[self._current_frame]
        self._picture.setPixmap(pixmap)
        self._picture.setGeometry(
            64 + self._generator.infos()['%s_%d' % (
                self._animation, self._current_frame
            )]['x'] * 32,
            64 + self._generator.infos()['%s_%d' % (
                self._animation, self._current_frame
            )]['y'] * 32,
            pixmap.width(), pixmap.height()
        )
        self._counter += 1
        conf = None
        frame_key = 'frame_%d' % self._current_frame
        for elem in self.conf[frame_key]:
            if elem.get('type', None) == 'conf':
                conf = elem
                break
        if conf is None:
            conf = {'type': 'conf'}
            self.conf[frame_key].append(conf)
        if self._counter >= conf.get('multiplier', 1):
            self._counter = 0
            self._current_frame += 1
            if self._current_frame >= len(self._frames_pixmaps):
                self._current_frame = 0
