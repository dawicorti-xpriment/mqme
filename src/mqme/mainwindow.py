# -*- coding: utf-8 *-*
import os
import json
import Queue
import Image
from PyQt4 import QtGui
from PyQt4 import QtCore
from xml.dom.minidom import parse

import settings
from mqme import utils
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

    def export_physics(self, sps_obj, id, directory):
        svg_path = os.path.join(directory, id + '.svg')
        if os.path.exists(svg_path):
            with open(svg_path) as raw_file:
                dom = parse(raw_file)
                root = dom.getElementsByTagName('svg')[0]
                image = root.getElementsByTagName('image')[0]
                width = float(image.getAttribute('width'))
                height = float(image.getAttribute('height'))
                x = float(image.getAttribute('x'))
                y = float(image.getAttribute('y'))
                for rect in root.getElementsByTagName('rect'):
                    physics_type = rect.getAttribute('id').split('_')[0]
                    if physics_type != 'platform':
                        physics_type = 'ground'
                    sps_obj['physics'][id].append({
                        'x': (float(rect.getAttribute('x')) - x) / width,
                        'y': (float(rect.getAttribute('y')) - y) / height,
                        'width': float(rect.getAttribute('width')) / width,
                        'height': float(rect.getAttribute('height')) / height,
                        'type': physics_type
                    })
                for circle in root.getElementsByTagName('path'):
                    sodipodi_type = circle.getAttribute('sodipodi:type')
                    if sodipodi_type == 'arc':
                        cx = float(circle.getAttribute('sodipodi:cx'))
                        transform_raw = circle.getAttribute('transform')
                        transform_raw = transform_raw.replace('translate(', '').replace(')', '')
                        foe_x = float(transform_raw.split(',')[0]) + cx
                        sps_obj['foes'][id].append({
                            'x': (foe_x - x) / width
                        })
                        if id.find('town_d') > -1:
                            print cx, transform_raw, foe_x, x, (foe_x - x) / width

    def export_fight_environments(self, directory):
        fightenv_directory = os.path.join(directory, 'fightenv')
        environments = self.config.current_file().get('fightenv', {})
        layers = ('background3', 'background2')
        for name, fight_env in environments.items():
            sps_obj = {'backgrounds': [], 'physics': {}, 'foes': {}}
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
                    sps_obj['physics'][name + '_' + image_id] = []
                    sps_obj['foes'][name + '_' + image_id] = []
                    self.export_physics(
                        sps_obj, name + '_' + image_id, os.path.dirname(image_path)
                    )
                    image = utils.get_resized_image(image_path)    
                    output_path = os.path.join(
                        fightenv_directory,
                        name + '_' + image_id + '.png'
                    )
                    image.save(output_path)
                    sps_obj['backgrounds'].append('fightenv/' + name + '_' + image_id)
            for layer_index in (2, 3):
                image = utils.get_resized_image(
                    self.config.current_file()['pathes'][
                        fight_env['background' + str(layer_index)]
                    ]
                )
                output_path = os.path.join(
                    fightenv_directory,
                    name + '_bg' + str(layer_index) + '.png'
                )
                image.save(output_path)
                sps_obj['backgrounds'].append(
                    'fightenv/' + name + '_bg' + str(layer_index)
                )
            base_path = os.path.join(fightenv_directory, name)
            with open(base_path + '.sps', 'w') as sps:
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
