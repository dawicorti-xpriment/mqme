# -*- coding: utf-8 *-*

import sys
from PyQt4 import QtGui
import settings

from mqme.mainwindow import MainWindow


def run():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow(
        settings.RESOLUTION,
        settings.FULL_APP_NAME
    )
    main_window.showMaximized()
    app.exec_()


if __name__ == '__main__':
    run()
