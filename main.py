import sys
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtCore

K1, K2 = 203.995, -11.998
# Координаты для проверки индекса: 47,216183 56,138722


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
        self.im = None
        self.mark_pos = None
        self.postal_code = ''
        self.address = ''

        self.show_map()
        self.btn_show_map.clicked.connect(self.show_map)
        self.size.valueChanged.connect(self.show_map)
        self.c1.valueChanged.connect(self.show_map)
        self.c2.valueChanged.connect(self.show_map)
        self.cb_layer.currentIndexChanged.connect(self.show_map)
        self.btn_seacrh.clicked.connect(self.search)
        self.btn_del_mark.clicked.connect(self.del_mark)
        self.cb_postal_code.stateChanged.connect(self.change_postal_code)

    def mousePressEvent(self, event):
        if event.button() not in (Qt.LeftButton, Qt.RightButton):
            return
        x, y = event.x(), event.y()
        if not (330 <= x <= 330 + 450 and 70 <= y <= 70 + 450):
            return
        size = self.size.value()
        c1 = self.c1.value()
        c2 = self.c2.value()
        spn = K1 / size + K2
        x0, y0 = c1 - spn / 2, c2 + spn / 2
        self.mark_pos = f'{x0 + (x - 330) * spn / 450},{y0 - (y - 70) * spn / 450}'
        self.show_map()
        self.show_address(*self.mark_pos.split(','), event.button() == Qt.RightButton)

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
        if self.mark_pos is not None:
            mark = f'&pt={self.mark_pos},pm2rdm'
        else:
            mark = ''
        request = f'https://static-maps.yandex.ru/1.x/?ll={c1},{c2}&size=450,450&spn={spn},{spn}&l={get_layer[layer]}' \
                  f'{mark}'
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
        self.show_address(c1, c2)

    def search(self):
        geocode = self.le_search.text()
        apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={apikey}&geocode={geocode}&format=json"
        response = requests.get(geocoder_request)
        if response:
            self.err.setText('')
            json_response = response.json()
            s = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            c1, c2 = s.split()
            self.mark_pos = ','.join((c1, c2))
            self.c1.setValue(float(c1))
            self.c2.setValue(float(c2))
        else:
            self.err.setText('Ошибка')
            print(response.content)

    def change_postal_code(self):
        address = self.address
        if self.cb_postal_code.isChecked():
            address = f"{self.postal_code} {self.address}"
        self.le_address.setText(address)

    def show_address(self, c1, c2, org_search=False):
        if org_search:
            search_api_server = "https://search-maps.yandex.ru/v1/"
            api_key = "99f9c994-307e-4fa7-b70c-5d6ef3439e7c"
            geocode = f'{c1},{c2}'
            search_params = {
                "apikey": api_key,
                "text": geocode,
                "lang": "ru_RU",
                "ll": geocode,
                "type": "biz",
                "spn": f"{50/111135},{50/111135}",
                "rspn": 1
            }
            response = requests.get(search_api_server, params=search_params)
            if not response:
                print(response.content)
                return
            json_response = response.json()
            try:
                organization = json_response["features"][0]
                org_name = organization["properties"]["CompanyMetaData"]["name"]
                self.le_address.setText(f'Организация: {org_name}')
            except Exception:
                self.le_address.setText('')
            return

        apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
        geocode = f'{c1},{c2}'
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={apikey}&geocode={geocode}&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            address = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']\
                ['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            try:
                postal_code = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']\
                    ['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']\
                    ['SubAdministrativeArea']['Locality']['Thoroughfare']['Premise']['PostalCode']['PostalCodeNumber']
            except Exception:
                postal_code = ''
            self.address = address
            self.postal_code = postal_code
            if self.cb_postal_code.isChecked():
                address = f"{postal_code} {address}"
            self.le_address.setText(address)
        else:
            print(response.content)

    def del_mark(self):
        self.mark_pos = None
        self.show_map()

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
