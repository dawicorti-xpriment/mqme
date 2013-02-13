# -*- coding: utf-8 *-*
import os
import json
import Queue
import Image
from PyQt4 import QtGui
from PyQt4 import QtCore

import settings
from mqme.menubar import MenuBar
from mqme.tileseditor import TilesEditor
from mqme.mapeditor import MapEditor
from mqme.layersdialog import LayersDialog
from mqme.spriteseditor import SpritesEditor
from mqme.spritesgenerator import SpritesGenerator
from mqme.fightenvironmenteditor import FightEnvironmentEditor
from mqme.config import Config


class MainWindow(QtGui.QMainWindow):

    resources_directories = (
        'fightenv', 'images', 'maps', 'sprites', 'tiles'
    )

    queue = Queue.Queue()

    CHILDREN = (
        TilesEditor, MapEditor,
        LayersDialog, SpritesEditor,
        FightEnvironmentEditor
    )

    def __init__(self, resolution, title):
        super(MainWindow, self).__init__()
        self.config = Config()
        self.config.init_from_file(settings.CONFIG_FILE_PATH)
        self._timer = QtCore.QTimer(self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(
            settings.IMAGES_PATH, 'mqme.png'
        )))
        MainWindow._subscriptions = {
            'config.save': self.on_save_config_request,
            'menu.trigger.save_project': self.on_save_project_request,
            'menu.trigger.new_project': self.on_new_project_request,
            'menu.trigger.open_project': self.on_open_project_request,
            'menu.trigger.export_to_resources': self.on_export_request
        }
        self.connect(self._timer, QtCore.SIGNAL("timeout()"), self.update)
        self.workspace = QtGui.QWorkspace()
        width, height = resolution
        self.resize(width, height)
        self.setWindowTitle(title)
        self.setCentralWidget(self.workspace)
        self.setMenuBar(MenuBar(self, self.on_menu_triggered))
        self._children = []
        for child_type in self.CHILDREN:
            child = child_type()
            self.workspace.addWindow(child)
            child.set_queue(MainWindow.queue)
            self._children.append(child)
        self._timer.start(settings.QUEUE_READ_LOOP_DELAY)

    def keyPressEvent(self, event):
        super(MainWindow, self).keyPressEvent(event)
        self.send('key_press', {'key': event.key()})

    def keyReleaseEvent(self, event):
        super(MainWindow, self).keyReleaseEvent(event)
        self.send('key_release', {'key': event.key()})

    def send(self, name, body=None):
        message = {'name': name}
        if body is not None:
            message.update(body)
        MainWindow.queue.put(message)

    @staticmethod
    def subscribe(message_name, callback):
        MainWindow._subscriptions[message_name] = callback

    def receive(self, message):
        name = message.get('name')
        if name in MainWindow._subscriptions:
            MainWindow._subscriptions[name](message)

    def on_menu_triggered(self, menu_name):
        self.send('menu.trigger.%s' % menu_name)

    def update(self):
        try:
            index = 0
            while index < settings.QUEUE_READ_LOOP_DELAY:
                message = MainWindow.queue.get_nowait()
                self.receive(message)
                for child in self._children:
                    child.receive(message)
                index += 1
        except Queue.Empty:
            pass

    def on_save_config_request(self, message):
        self.config.save(settings.CONFIG_FILE_PATH)

    def on_save_project_request(self, message):
        file_name = QtGui.QFileDialog.getSaveFileName(
            self, filter='MQME Projects (*.mqp)',
            directory=self.config.get(
                'project_dir', os.path.expanduser('~')
            )
        )
        if file_name:
            file_name = unicode(file_name)
            self.config.set(
                'project_dir', os.path.dirname(file_name)
            )
            self.config.save(settings.CONFIG_FILE_PATH)
            self.config.save_current_file(file_name)

    def on_open_project_request(self, message):
        file_name = QtGui.QFileDialog.getOpenFileName(
            self, filter='MQME Projects (*.mqp)',
            directory=self.config.get(
                'project_dir', os.path.expanduser('~')
            )
        )
        if file_name:
            self.send('new_project')
            file_name = unicode(file_name)
            self.config.set(
                'project_dir', os.path.dirname(file_name)
            )
            self.config.save(settings.CONFIG_FILE_PATH)
            self.config.read_current_file(file_name)
            self.send('open_project')

    def on_new_project_request(self, message):
        self.config.reset_current_file()
        self.send('new_project')

    def on_export_request(self, message):
        if self.config.has_changed():
            msg_box = QtGui.QMessageBox(self)
            msg_box.setWindowTitle('Config has changed')
            msg_box.setText(
                'You need to save the project before exporting'
            )
            msg_box.setDefaultButton(QtGui.QMessageBox.Cancel)
            msg_box.exec_()
            return
        current_file = self.config.current_file()
        directory = None
        if 'pathes' in current_file:
            directory = current_file['pathes'].get('resources_dir', None)
        if directory is None:
            directory = QtGui.QFileDialog.getExistingDirectory(
                self, directory=self.config.get(
                    'resources_dir', os.path.expanduser('~')
                )
            )
        if directory is not None:
            directory = str(directory)
            if not 'pathes' in current_file:
                current_file['pathes'] = {}
            current_file['pathes']['resources_dir'] = directory
            self.config.set('resources_dir', directory)
            self.config.save(settings.CONFIG_FILE_PATH)
            for sub_directory in self.resources_directories:
                subpath = os.path.join(directory, sub_directory)
                if not os.path.exists(subpath):
                    os.makedirs(subpath)
            self.export_maps(directory)
            self.export_tilesets(directory)
            self.export_sprites(directory)
            self.export_fight_environments(directory)
            msg_box = QtGui.QMessageBox(self)
            msg_box.setWindowTitle('Export')
            msg_box.setText(
                'Project exported successfully !'
            )
            msg_box.setDefaultButton(QtGui.QMessageBox.Cancel)
            msg_box.exec_()

    def export_fight_environments(self, directory):
        fightenv_directory = os.path.join(directory, 'fightenv')
        environments = self.config.current_file().get('fightenv', {})
        layers = ('background3', 'background2')
        for name, fight_env in environments.items():
            max_width = 0
            max_height = 0
            images = {}
            bg1_path = self.config.current_file()['pathes'][
                fight_env['background1']
            ]
            bg1_key = os.path.basename(bg1_path).split('_')[0]
            bg1_directory = os.path.dirname(bg1_path)
            for image_name in os.listdir(bg1_directory):
                if image_name.startswith(bg1_key) and image_name.endswith('.png'):
                    image_id = image_name.split('_', 1)[1].split('.')[0]
                    image_path = os.path.join(bg1_directory, image_name)
                    images[image_id] = Image.open(image_path)
                    width, height = images[image_id].size
                    max_width += width
                    if max_height < height:
                        max_height = height
            sps_obj = {}
            crop_x = 0
            image = Image.new('RGBA', (max_width, max_height))
            for image_name in images:
                width, height = images[image_name].size
                sps_obj[image_name] = {
                    'crop_x': crop_x,
                    'crop_y': 0,
                    'crop_width': width,
                    'crop_height': height
                }
                image.paste(images[image_name], (crop_x, 0))
                crop_x += width
            base_path = os.path.join(fightenv_directory, name)
            image.save(base_path + '_bg1.png')
            with open(base_path + '_bg1.sps', 'w') as sps:
                sps.write(json.dumps(sps_obj))
            for layer_index in (2, 3):
                image = Image.open(
                    self.config.current_file()['pathes'][
                        fight_env['background' + str(layer_index)]
                    ]
                )
                width, height = image.size
                image.save(base_path + '_bg' + str(layer_index) + '.png')
                sps_obj = {}
                sps_obj['background' + str(layer_index)] = {
                    'crop_x': 0,
                    'crop_y': 0,
                    'crop_width': width,
                    'crop_height': height
                }
                with open(base_path + '_bg' + str(layer_index) + '.sps', 'w') as sps:
                    sps.write(json.dumps(sps_obj))

    def export_sprites(self, directory):
        sprites_directory = os.path.join(directory, 'sprites')
        actors = self.config.current_file().get('actors', {})
        for actor_name in actors:
            SpritesGenerator(actor_name).save(sprites_directory)

    def export_maps(self, directory):
        maps = self.config.current_file().get('maps', {})
        for map_name, map_obj in maps.items():
            path = os.path.join(directory, 'maps', map_name + '.map')
            map_obj['camera'] = [
                map_obj['camera_width'],
                map_obj['camera_height']
            ]
            map_obj['size'] = [
                map_obj['width'],
                map_obj['height']
            ]
            x = 0
            for matrix_line in map_obj['specials']:
                y = 0
                for special_conf in matrix_line:
                    if special_conf['class_name'] == 'start_pos':
                        map_obj['start_pos'] = [x, y]
                    y += 1
                x += 1
            with open(path, 'w') as map_file:
                map_file.write(json.dumps(map_obj, sort_keys=True, indent=4))

    def export_tilesets(self, directory):
        tilesets = self.config.current_file().get('tilesets', {})
        for tileset_name, tileset_obj in tilesets.items():
            path = os.path.join(directory, 'tiles', tileset_name + '.sps')
            with open(path, 'w') as tileset_file:
                tileset_file.write(json.dumps(
                    tileset_obj, sort_keys=True, indent=4
                ))
