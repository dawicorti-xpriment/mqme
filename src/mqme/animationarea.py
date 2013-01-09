# -*- coding: utf-8 *-*
import os
import uuid
from PyQt4 import QtGui

from mqme.spritegridwidget import SpriteGridWidget
from mqme.iconbutton import IconButton
from mqme.config import Config
from mqme.frameimage import FrameImage
from mqme.animationpreview import AnimationPreview


class AnimationArea(QtGui.QFrame):

    FPS_VALUES = [40, 35, 30, 25, 20, 15, 10, 5, 2, 1]
    NB_MULTIPLIERS = 100

    def __init__(self, parent, actor_name, animation_name):
        super(AnimationArea, self).__init__(parent)
        self._parent = parent
        self.config = Config()
        self.current_conf = Config().current_file()[
            'actors'
        ][actor_name]['animations'][animation_name]
        self._current_frame = 0
        self._actor_name = actor_name
        self._animation_name = animation_name
        self.setGeometry(0, 0, 480, 450)
        self._frames_list = QtGui.QComboBox(self)
        self._frames_list.setGeometry(5, 420, 100, 20)
        self._frames_list.currentIndexChanged.connect(self.on_change_frame)
        self._add_frame_button = IconButton(self, 'add_frame', 50, 50)
        self._add_frame_button.setGeometry(110, 420, 20, 20)
        self._add_frame_button.clicked.connect(self.on_add_frame)
        self._remove_frame_button = IconButton(self, 'remove_frame', 50, 50)
        self._remove_frame_button.setGeometry(135, 420, 20, 20)
        self._remove_frame_button.clicked.connect(self.on_remove_frame)
        self._scroll_areas = {}
        self._add_picture_button = IconButton(self, 'add_picture', 50, 50)
        self._add_picture_button.setGeometry(402, 2, 50, 50)
        self._add_picture_button.clicked.connect(self.on_new_picture)
        self._remove_animation_button = IconButton(
            self, 'remove_animation', 50, 50
        )
        self._remove_animation_button.setGeometry(402, 54, 50, 50)
        self._remove_animation_button.clicked.connect(self.on_remove_animation)
        self._resize_button = QtGui.QRadioButton('Resize', self)
        self._resize_button.setGeometry(170, 420, 70, 20)
        self._move_button = QtGui.QRadioButton('Move', self)
        self._move_button.setGeometry(240, 420, 70, 20)
        self._move_button.setChecked(True)
        self._multiplier = QtGui.QComboBox(self)
        self._multiplier.setGeometry(402, 380, 50, 20)
        for multiplier in range(1, self.NB_MULTIPLIERS + 1):
            self._multiplier.addItem('x' + str(multiplier))
        self._pos_label = QtGui.QLabel(self)
        self._pos_label.setGeometry(402, 100, 50, 100)
        self._play_animation = IconButton(self, 'play_animation', 50, 50)
        self._play_animation.setGeometry(402, 210, 50, 50)
        self._play_animation.clicked.connect(self.on_play_animation)
        self._fps_choice = QtGui.QComboBox(self)
        self._fps_choice.setGeometry(310, 420, 150, 20)
        if not len(self.current_conf):
            self._scroll_areas[0] = QtGui.QScrollArea(self)
            self._scroll_areas[0].setGeometry(0, 0, 400, 400)
            self._scroll_areas[0].setWidget(SpriteGridWidget(self))
            self._frames_list.addItem('Frame 0')
            self.current_conf['fps'] = 40
        for value in self.FPS_VALUES:
            period = 1000 / value
            self._fps_choice.addItem('%d FPS - %d ms' % (value, period))
        self._fps_choice.setCurrentIndex(self.FPS_VALUES.index(
            self.current_conf['fps']
        ))
        self._fps_choice.currentIndexChanged.connect(self.on_change_fps)
        self._multiplier.currentIndexChanged.connect(self.on_change_multiplier)

    def on_change_multiplier(self):
        frame_key = 'frame_%d' % self._current_frame
        conf = None
        for elem in self.current_conf[frame_key]:
            if elem.get('type', None) == 'conf':
                conf = elem
                break
        if conf is None:
            conf = {'type': 'conf'}
            self.current_conf[frame_key].append(conf)
        multiplier = self._multiplier.currentIndex() + 1
        conf['multiplier'] = multiplier

    def on_play_animation(self):
        preview = AnimationPreview(
            self, self._actor_name, self._animation_name
        )
        preview.show()

    def read_conf(self):
        for index in range(len(self.current_conf) - 1):
            frame_key = 'frame_%d' % index
            self._scroll_areas[index] = QtGui.QScrollArea(self)
            self._scroll_areas[index].setGeometry(0, 0, 400, 400)
            self._scroll_areas[index].setWidget(SpriteGridWidget(self))
            for obj in self.current_conf[frame_key]:
                if obj.get('type', None) != 'conf':
                    frame_image = FrameImage(
                        self._scroll_areas[index].widget(),
                        self.config.current_file()['pathes'][obj['id']],
                        obj['id'], frame_key
                    )
                    frame_image.setGeometry(
                        200 + obj['x'] * 100,
                        200 + obj['y'] * 100,
                        obj['width'] * 100,
                        obj['height'] * 100,
                    )
                    frame_image.show()
                    self._frames_list.addItem('Frame %d' % index)
            self._scroll_areas[index].hide()
        self._current_frame = 0
        self._scroll_areas[0].show()
        self._frames_list.setCurrentIndex(0)
        frame_key = 'frame_%d' % self._current_frame
        conf = None
        for elem in self.current_conf[frame_key]:
            if elem.get('type', None) == 'conf':
                conf = elem
                break
        if conf is None:
            conf = {'type': 'conf'}
            self.current_conf[frame_key].append(conf)
        multiplier = conf.get('multiplier', 1)
        self._multiplier.setCurrentIndex(multiplier - 1)

    def remove_animation(self):
        animations = Config().current_file()[
            'actors'][self._actor_name]['animations']
        del animations[self._animation_name]

    def on_remove_animation(self):
        self._parent.remove_animation(self._animation_name)

    def on_change_fps(self):
        self.current_conf['fps'] = self.FPS_VALUES[
            self._fps_choice.currentIndex()
        ]

    def on_remove_frame(self):
        if len(self._scroll_areas) > 1:
            if self._current_frame == len(self._scroll_areas) - 1:
                frame_key = self.get_frame_key()
                if frame_key in self.current_conf:
                    del self.current_conf[frame_key]
                self._scroll_areas[self._current_frame].hide()
                del self._scroll_areas[self._current_frame]
                self._current_frame -= 1
                self._frames_list.setCurrentIndex(self._current_frame)
                self._frames_list.removeItem(len(self._scroll_areas))

    def move_image(self, image, gap):
        gap_x, gap_y = gap
        obj = None
        rect = image.geometry()
        for image_obj in self.current_conf[image.frame_key()]:
            if image_obj.get('type', None) != 'conf':
                if image_obj['id'] == image.image_id():
                    obj = image_obj
        if self._move_button.isChecked():
            x, y = rect.x() + gap_x, rect.y() + gap_y
            image.setGeometry(x, y, rect.width(), rect.height())
            obj['x'] = (x - 200.0) / 100.0
            obj['y'] = (y - 200.0) / 100.0
        else:
            width = rect.width() + gap_x
            height = width * rect.height() / rect.width()
            image.setGeometry(rect.x(), rect.y(), width, height)
            obj['width'] = width / 100.0
            obj['height'] = height / 100.0
        self.update_label(obj)

    def update_label(self, image_obj):
        self._pos_label.setText(
            'X : %s\nY : %s\nW : %s\nH : %s' % (
                str(image_obj['x']),
                str(image_obj['y']),
                str(image_obj['width']),
                str(image_obj['height'])
            )
        )

    def on_change_frame(self):
        self._scroll_areas[self._current_frame].hide()
        self._current_frame = self._frames_list.currentIndex()
        frame_key = 'frame_%d' % self._current_frame
        if frame_key in self.current_conf:
            conf = None
            for elem in self.current_conf.get(frame_key, []):
                if elem.get('type', None) == 'conf':
                    conf = elem
                    break
            if conf is None:
                conf = {'type': 'conf'}
                self.current_conf[frame_key].append(conf)
            multiplier = conf.get('multiplier', 1)
        else:
            multiplier = 1
        self._multiplier.setCurrentIndex(multiplier - 1)
        self._scroll_areas[self._current_frame].show()

    def on_add_frame(self):
        if self._current_frame == len(self._scroll_areas) - 1:
            self._scroll_areas[self._current_frame].hide()
            self._current_frame += 1
            frame_label = 'Frame %d' % self._current_frame
            self._scroll_areas[self._current_frame] = QtGui.QScrollArea(self)
            self._scroll_areas[self._current_frame].setGeometry(0, 0, 400, 400)
            self._scroll_areas[self._current_frame].setWidget(
                SpriteGridWidget(self)
            )
            self._frames_list.addItem(frame_label)
            self._frames_list.setCurrentIndex(self._current_frame)
            frame_key = self.get_frame_key()
            if not frame_key in self.current_conf:
                self.current_conf[frame_key] = []

    def get_frame_key(self):
        return 'frame_%d' % self._current_frame

    def remove_image(self, frame_image):
        frame_image.hide()
        index = 0
        for image_obj in self.current_conf[frame_image.frame_key()]:
            if image_obj['id'] == frame_image.image_id():
                self.current_conf[frame_image.frame_key()].pop(index)
            index += 1

    def on_new_picture(self):
        file_name = QtGui.QFileDialog.getOpenFileName(
            self, filter='Image (*.png)',
            directory=self.config.get(
                'frame_image_dir', os.path.expanduser('~')
            )
        )
        if file_name:
            from mqme.mainwindow import MainWindow
            file_name = unicode(file_name)
            self.config.set('frame_image_dir', os.path.dirname(file_name))
            MainWindow.queue.put({'name': 'config.save'})
            if not 'pathes' in Config().current_file():
                Config().current_file()['pathes'] = {}
            image_id = str(uuid.uuid1())
            Config().current_file()['pathes'][image_id] = file_name
            frame_key = self.get_frame_key()
            if not frame_key in self.current_conf:
                self.current_conf[frame_key] = []
            frame_image = FrameImage(
                self._scroll_areas[self._current_frame].widget(),
                file_name, image_id, frame_key
            )
            frame_image.show()
            width, height = frame_image.ratio()
            x = 0.5 - (width / 2.0)
            y = 1.0 - height
            self.current_conf[frame_key].append({
                'id': image_id,
                'width': width, 'height': height,
                'x': x, 'y': y
            })
            frame_image.setGeometry(
                200 + x * 100, 200 + y * 100, width * 100, height * 100
            )
