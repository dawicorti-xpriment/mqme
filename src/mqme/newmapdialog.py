# -*- coding: utf-8 *-*
from PyQt4 import QtGui


class NewMapDialog(QtGui.QDialog):

    def __init__(self, parent):
        super(NewMapDialog, self).__init__(parent)
        self.setModal(True)
        self.setGeometry(
            (parent.width() - 200) / 2,
            (parent.height() - 500) / 2,
            300, 350
        )
        self.data = None
        self.setWindowTitle('New map')
        QtGui.QLabel("Name :", self).setGeometry(20, 10, 150, 20)
        QtGui.QLabel("Width :", self).setGeometry(20, 70, 150, 20)
        QtGui.QLabel("Height :", self).setGeometry(20, 130, 150, 20)
        QtGui.QLabel("Camera Width :", self).setGeometry(20, 190, 150, 20)
        QtGui.QLabel("Camera Height :", self).setGeometry(20, 250, 150, 20)
        self._name = QtGui.QLineEdit(self)
        self._name.setGeometry(140, 10, 150, 20)
        self._width = QtGui.QLineEdit('120', self)
        self._width.setGeometry(140, 70, 150, 20)
        self._height = QtGui.QLineEdit('80', self)
        self._height.setGeometry(140, 130, 150, 20)
        self._camera_width = QtGui.QLineEdit('12', self)
        self._camera_width.setGeometry(140, 190, 150, 20)
        self._camera_height = QtGui.QLineEdit('8', self)
        self._camera_height.setGeometry(140, 250, 150, 20)
        self._ok = QtGui.QPushButton('OK', self)
        self._ok.setGeometry(220, 325, 70, 20)
        self._ok.clicked.connect(self.on_accept)
        self._cancel = QtGui.QPushButton('Cancel', self)
        self._cancel.setGeometry(140, 325, 70, 20)
        self._cancel.clicked.connect(self.hide)

    @staticmethod
    def get_new_map(parent):
        dialog = NewMapDialog(parent)
        dialog.exec_()
        return dialog.data

    def get_data(self):
        data = {}
        if len(str(self._name.text())) == 0:
            raise ValueError
        data['name'] = str(self._name.text())
        data['width'] = int(self._width.text())
        data['height'] = int(self._height.text())
        data['camera_width'] = int(self._camera_width.text())
        data['camera_height'] = int(self._camera_height.text())
        return data

    def on_accept(self):
        data = None
        try:
            data = self.get_data()
        except:
            data = None
        self.data = data
        self.hide()

    def on_cancel(self):
        self.data = None
        self.hide()
