# -*- coding: utf-8 *-*
import os
import Image
import json
from mqme.config import Config


class SpritesGenerator(object):

    def __init__(self, actor_name):
        self._actor_name = actor_name
        self.current_conf = Config().current_file()['actors'][actor_name]
        self._sps_infos = {}
        self._crop_x = 0
        self._crop_y = 0

    def save(self, directory):
        animation_images = {}
        width = 0
        for animation_name in self.current_conf.get('animations', {}):
            animation_images[animation_name] = self.get_animation_as_image(
                animation_name
            )
            im_width, im_height = animation_images[animation_name].size
            if width < im_width:
                width = im_width
        sprites_image = Image.new('RGBA', (width, self._crop_y))
        y_offset = 0
        for animation_name in self.current_conf.get('animations', {}):
            sprites_image.paste(
                animation_images[animation_name], (0, y_offset)
            )
            im_width, im_height = animation_images[animation_name].size
            y_offset += im_height
        base_path = os.path.join(directory, self._actor_name)
        sprites_image.save(base_path + '.png')
        with open(base_path + '.sps', 'w') as sps:
            sps.write(json.dumps(self._sps_infos))

    def infos(self):
        return self._sps_infos

    def get_animation_as_image(self, animation_name):
        self._crop_x = 0
        max_crop_height = 0
        n_frame = len(self.current_conf['animations'][animation_name]) - 1
        self._sps_infos[animation_name] = {
            'fps': self.current_conf['animations'][animation_name]['fps'],
            'count': n_frame
        }
        frames_images = {}
        for frame_index in range(n_frame):
            frames_images[frame_index] = self.get_frame_as_image(
                animation_name, frame_index
            )
            current_sps = self._sps_infos[
                '%s_%s' % (animation_name, frame_index)
            ]
            current_sps.update({
                'crop_x': self._crop_x,
                'crop_y': self._crop_y,
                'crop_width': int(current_sps['width'] * 32),
                'crop_height': int(current_sps['height'] * 32),
            })
            if max_crop_height < current_sps['crop_height']:
                max_crop_height = current_sps['crop_height']
            self._crop_x += current_sps['crop_width']
        animation_image = Image.new('RGBA', (self._crop_x, max_crop_height))
        for frame_index in range(n_frame):
            current_sps = self._sps_infos[
                '%s_%s' % (animation_name, frame_index)
            ]
            animation_image.paste(frames_images[frame_index], (
                current_sps['crop_x'], 0
            ))
        self._crop_y += max_crop_height
        return animation_image

    def get_frame_as_image(self, animation_name, frame_index):
        frame_key = 'frame_%d' % frame_index
        if not len(self.current_conf['animations'][animation_name][frame_key]):
            return None
        left = None
        top = None
        right = None
        bottom = None
        conf = None
        for obj in self.current_conf['animations'][animation_name][frame_key]:
            if obj.get('type', None) != 'conf':
                if left is None or left > obj['x']:
                    left = obj['x']
                if top is None or top > obj['y']:
                    top = obj['y']
                if right is None or right < obj['x'] + obj['width']:
                    right = obj['x'] + obj['width']
                if bottom is None or bottom < obj['y'] + obj['height']:
                    bottom = obj['y'] + obj['height']
        image = Image.new('RGBA', (
            int((right - left) * 32), int((bottom - top) * 32)
        ))
        for obj in self.current_conf['animations'][animation_name][frame_key]:
            if obj.get('type', None) != 'conf':
                sub_image = Image.open(
                    Config().current_file()['pathes'][obj['id']]
                )
                sub_image = sub_image.resize(
                    (int(obj['width'] * 32), int(obj['height'] * 32))
                )
                image.paste(sub_image, (
                    int((obj['x'] - left) * 32), int((obj['y'] - top) * 32)
                ))
            else:
                conf = obj
        self._sps_infos['%s_%s' % (animation_name, frame_index)] = {
            'x': left,
            'y': top,
            'width': right - left,
            'height': bottom - top
        }
        if conf is not None:
            self._sps_infos[
                '%s_%s' % (animation_name, frame_index)
            ].update(conf)
        return image
