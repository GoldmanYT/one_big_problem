import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtCore


K1, K2 = 203.995, -11.998


class KeyHelper(QtCore.QObject):
    keyPressed = QtCore.pyqtSignal(QtCore.Qt.Key)

    def __init__(self, window):
        super().__init__(window)
        self._window = window

        self.window.installEventFilter(self)

    @property
    def window(self):
        return self._window

    def eventFilter(self, obj, event):
        if obj is self.window and event.type() == QtCore.QEvent.KeyPress:
            self.keyPressed.emit(event.key())
        return super().eventFilter(obj, event)


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui.ui', self)
        self.show_map()
        self.btn_show_map.clicked.connect(self.show_map)
        self.size.valueChanged.connect(self.show_map)
        self.c1.valueChanged.connect(self.show_map)
        self.c2.valueChanged.connect(self.show_map)
        self.cb_layer.currentIndexChanged.connect(self.show_map)
        self.im = None

    def show_map(self):
        size = self.size.value()
        c1 = self.c1.value()
        c2 = self.c2.value()
        layer = self.cb_layer.currentIndex()
        get_layer = {
            0: 'map',
            1: 'sat',
            2: 'sat,skl'
        }
        spn = K1 / size + K2
        request = f'https://static-maps.yandex.ru/1.x/?ll={c1},{c2}&size=450,450&spn={spn},{spn}&l={get_layer[layer]}'
        response = requests.get(request)
        if response:
            self.err.setText('')
            with open('res.png', 'wb') as f:
                f.write(response.content)
            self.im = QPixmap('res.png')
            self.res.setPixmap(self.im)
        else:
            self.err.setText('Ошибка')
            print(response.content)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            self.keyPressed.emit(event.key())
        return super().eventFilter(obj, event)

    def keyPressEvent(self, key):
        if key == Qt.Key_PageDown:
            self.size.setValue(self.size.value() - 1)
        if key == Qt.Key_PageUp:
            self.size.setValue(self.size.value() + 1)
        spn = K1 / self.size.value() + K2
        if key == Qt.Key_Up:
            self.c2.setValue(self.c2.value() + spn)
        if key == Qt.Key_Down:
            self.c2.setValue(self.c2.value() - spn)
        if key == Qt.Key_Left:
            self.c1.setValue(self.c1.value() - spn)
        if key == Qt.Key_Right:
            self.c1.setValue(self.c1.value() + spn)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()

    helper = KeyHelper(ex.windowHandle())
    helper.keyPressed.connect(ex.keyPressEvent)

    sys.excepthook = except_hook
    sys.exit(app.exec())
