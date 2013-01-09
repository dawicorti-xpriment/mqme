# -*- coding: utf-8 *-*
import json
import os
from copy import deepcopy


class Config(object):

    _instance = None

    def __new__(self):
        if self._instance is None:
            self._instance = object.__new__(self)
            self._instance._initialize()
        return self._instance

    def _initialize(self):
        self._dict = {}
        self._cache = {}
        self._dict['reference'] = {}

    def set(self, name, value):
        self._dict[name] = value

    def get(self, name, default):
        return self._dict.get(name, default)

    def init_from_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path) as input_file:
                self._dict = json.loads(input_file.read())
                self._dict['current_file'] = {}

    def save(self, file_path):
        with open(file_path, 'w') as output_file:
            output_file.write(json.dumps(self._dict))

    def current_file(self):
        if not 'current_file' in self._dict:
            self._dict['current_file'] = {}
        return self._dict['current_file']

    def save_current_file(self, file_path):
        for name, path in self._dict['current_file'].get('pathes', {}).items():
            self._dict['current_file']['pathes'][name] = os.path.relpath(
                path, os.path.dirname(file_path)
            ).replace('\\', '/')
        with open(file_path, 'w') as output_file:
            output_file.write(json.dumps(
                self._dict['current_file'], sort_keys=True, indent=4
            ))
        for name, path in self._dict['current_file'].get('pathes', {}).items():
            rel_path = path.replace('/', os.path.sep)
            self._dict['current_file']['pathes'][name] = os.path.abspath(
                os.path.join(os.path.dirname(file_path), rel_path)
            )
        self._dict['reference'] = deepcopy(self._dict['current_file'])

    def read_current_file(self, file_path):
        with open(file_path) as input_file:
            self._dict['current_file'] = json.loads(input_file.read())
        for name, path in self._dict['current_file'].get('pathes', {}).items():
            rel_path = path.replace('/', os.path.sep)
            self._dict['current_file']['pathes'][name] = os.path.abspath(
                os.path.join(os.path.dirname(file_path), rel_path)
            )
        self._dict['reference'] = deepcopy(self._dict['current_file'])

    def has_changed(self):
        return self._dict['reference'] != self._dict['current_file']

    def reset_current_file(self):
        self._dict['current_file'] = {}

    def set_cache(self, var, value):
        self._cache[var] = value

    def get_cache(self, var):
        return self._cache[var]
