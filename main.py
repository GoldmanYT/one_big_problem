import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui.ui', self)
        self.show_map()
        self.btn_show_map.clicked.connect(self.show_map)
        self.size.valueChanged.connect(self.show_map)
        self.c1.valueChanged.connect(self.show_map)
        self.c2.valueChanged.connect(self.show_map)
        self.im = None

    def show_map(self):
        size = int(self.size.value())
        c1 = self.c1.value()
        c2 = self.c2.value()
        request = f'https://static-maps.yandex.ru/1.x/?ll={c1},{c2}&size=450,450&z={size}&l=map'
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.size.setValue(self.size.value() - 1)
        if event.key() == Qt.Key_PageUp:
            self.size.setValue(self.size.value() + 1)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
