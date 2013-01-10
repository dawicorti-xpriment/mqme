import os
import settings

from esky import bdist_esky
from distutils.core import setup

class PathWalker(object):

    def __init__(self, base_dir_name, base_path):
        self.__base_dir_name = base_dir_name
        self.__base_path = base_path
        self.__dirs = {}

    def walk_zmq_path(self, arg, dir_name, file_names):
        dir_target_name = self.__base_dir_name + dir_name.replace(self.__base_path, '')
        if not dir_target_name in self.__dirs:
            self.__dirs[dir_target_name] = []
        for file_name in file_names:
            file_path = os.path.join(dir_name, file_name)
            if os.path.isfile(file_path):
                self.__dirs[dir_target_name].append(file_path)

    def get_target_dirs(self):
        os.path.walk(self.__base_path, self.walk_zmq_path, None)
        return [list(i) for i in self.__dirs.items()]

setup(
    name=settings.APP_NAME,
    version=settings.VERSION,
    scripts=['MQME.py'],
    options={
        'bdist_esky': {
            'includes': [
                'PyQt4',
                'mqme',
                'sip'
            ]
        }
    },
    data_files=PathWalker(
        'assets',
        os.path.join(
            settings.APP_PATH,
            'assets'
        )
    ).get_target_dirs()
)
print PathWalker(
        'assets',
        os.path.join(
            settings.APP_PATH,
            'assets'
        )
    ).get_target_dirs()