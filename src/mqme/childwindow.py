# -*- coding: utf-8 *-*
from PyQt4 import QtGui


class ChildWindow(QtGui.QDialog):

    def __init__(self):
        super(ChildWindow, self).__init__()
        self._queue = None
        self._subscriptions = {}

    def subscribe(self, message, callback):
        self._subscriptions[message] = callback

    def set_queue(self, queue):
        self._queue = queue

    def send(self, name, body=None):
        if self._queue:
            message = {'name': name}
            if body is not None:
                message.update(body)
            self._queue.put(message)

    def receive(self, message):
        name = message.get('name')
        if name in self._subscriptions:
            self._subscriptions[name](message)

    def closeEvent(self, event):
        event.ignore()
        self.showMinimized()
