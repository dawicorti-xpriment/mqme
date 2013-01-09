from PyQt4 import QtGui

from mqme.menuaction import MenuAction


class MenuBar(QtGui.QMenuBar):

    MENUS_DESCRIPTIONS = [
        {'name': 'File', 'items': [
            {'name': 'New Project'},
            {'name': 'Open Project'},
            {'name': 'Save Project'},
            {'name': 'Export To Resources'},
        ]},
        {'name': 'Edit', 'items': [
            {'name': 'New Map'},
            {'name': 'New Actor'},
            {'name': 'New Fight Environment'},
            {'name': 'Import tileset'},
        ]},
    ]

    def __init__(self, parent, callback):
        super(MenuBar, self).__init__(parent)
        self._callback = callback
        for desc in self.MENUS_DESCRIPTIONS:
            self.create_menu(self, desc)
        self.show()

    def create_menu(self, parent, desc):
        if desc.get('items', None) or parent is self:
            menu = QtGui.QMenu(parent)
            menu.setTitle(desc['name'])
            parent.addMenu(menu)
        else:
            action = MenuAction(
                parent, desc['name'], self._callback
            )
            parent.addAction(action)
        for item in desc.get('items', []):
            self.create_menu(menu, item)
