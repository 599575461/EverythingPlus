import os
import re
import json
import base64

from Crypto.Cipher import AES
from requests import get
from playsound import playsound
from PyQt5 import QtWidgets, QtCore
from sys import exit, argv
from MainWindow import Ui_MainWindow
from ChildWindows import Ui_child_windows


class My_Windows(QtWidgets.QMainWindow, Ui_MainWindow, Ui_child_windows):

    def __init__(self):
        # 继承
        super(My_Windows, self).__init__()

        # 定义变量 数组
        self.search_name_list = ['名字']
        self.search_file_list = ['路径']
        self.search_size_list = ['大小']

        self.choose_file = list()
        self.text = str()

        # 创建文件路径变量
        self.dir_file = os.path.expanduser('~') + "\\Documents\\English_learn\\"
        json_file = self.dir_file + "data_key.json"

        # 判断目录
        if not os.path.exists(self.dir_file):
            os.makedirs(self.dir_file)

        # 判断文件
        if not os.path.isfile(json_file):
            with open(json_file, "w+") as w:
                json.dump({"key": 1}, w)
        # 加载json
        with open(json_file, "r") as w:
            self.password = str(json.load(w)["key"])

        # 设置子窗口和主窗口
        self.setupUi(self)
        self.Child_windows = QtWidgets.QDialog()
        self.Child_windows.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

        self.treeView.setModel(QtWidgets.QDirModel())
        self.treeView.setSortingEnabled(True)

    def info_message(self, title, text):
        QtWidgets.QMessageBox.information(self, title, text, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                          QtWidgets.QMessageBox.Yes)

    def search_file(self):
        # 调用Everything进行搜索

        text = self.file_name_search.text()

        if text == '':
            self.info_message('输入为空', '您必须输入东西才能搜索')
        else:
            file = os.popen(
                f'{os.path.splitdrive(os.getcwd())[0]} & cd {os.getcwd()}\\bin\\ & es.exe -s {text}').read().splitlines()

            if not file:
                self.info_message('基于Everything', '您必须启动Everything才能进行搜索')
            else:
                # 设置子窗口
                self.Child_windows.setWindowModality(QtCore.Qt.ApplicationModal)
                self.setupUi_(self.Child_windows)

                for i in range(len(file)):
                    name = file[i]
                    search = re.search(r'^[\s\S]*\.(txt|log|py|html|ini|json|c|cpp|yml|bat|xml|qss|qrc|qml)$', name)
                    if search:
                        self.search_name_list.append(name.split('\\')[-1])
                        self.search_file_list.append(name)

                # 名字
                Model_name = QtCore.QStringListModel()
                Model_name.setStringList(self.search_name_list)
                self.search_name.setModel(Model_name)

                # 路径
                Model_file = QtCore.QStringListModel()
                Model_file.setStringList(self.search_file_list)
                self.search_file_.setModel(Model_file)

                # 点击
                self.search_name.clicked.connect(self.list_clicked)

                # 子窗口循环显示
                self.Child_windows.show()
                self.Child_windows.exec_()

    def Edit_text(self, Text: str):
        self.compose.setPlainText(Text)

    def find_sound(self, isTxt=False):

        if not isTxt:
            word = self.English_txt.text()
        else:
            word = self.text

        if word == '' and not isTxt:
            self.info_message('输入为空', '您必须输入东西才能发音')
        elif isTxt:
            self.info_message('空', '您没有选取任何文件')
        else:
            file_name = f'{self.dir_file + word}.mp3'

            mp3 = get(url=f"https://tts.youdao.com/fanyivoice?word={word}&le=eng&keyfrom=speaker-target")

            with open(file_name, 'wb') as w:
                w.write(mp3.content)

            playsound(file_name)

    def clear_ca(self):
        for i in os.listdir(self.dir_file):
            if os.path.splitext(i)[1] == '.mp3':
                os.unlink(self.dir_file + i)

    def list_clicked(self, qModelIndex):
        try:
            self.choose_file.append(self.search_file_list[qModelIndex.row()])
            with open(self.choose_file[-1], 'r', encoding='UTF-8') as f:
                self.text = f.read()
                self.Edit_text(self.text)
        except FileNotFoundError:
            self.info_message('你在点哪', '路径和名字别瞎点')

    def closeEvent(self, event) -> None:
        self.clear_ca()

    def txt_dn(self):
        with open(self.choose_file[-1], 'r', encoding='utf-8') as banks:
            text = banks.read()
        aes = AES.new(add_to_16(self.password), AES.MODE_ECB)
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8')
        decrypted_text = base64.b64decode(decrypted_text.encode('utf-8')).decode('utf-8')
        with open(self.choose_file[-1], 'w', encoding='utf-8') as dn:
            dn.write(decrypted_text)

    def txt_en(self):
        with open(self.choose_file[-1], 'r', encoding='utf-8') as banks:
            my_str = banks.read()
        text = base64.b64encode(my_str.encode('utf-8')).decode('ascii')
        aes = AES.new(add_to_16(self.password), AES.MODE_ECB)
        encrypt_aes = aes.encrypt(add_to_16(text))
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
        with open(self.choose_file[-1], 'w', encoding='utf-8') as dn:
            dn.write(encrypted_text)


def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)


class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name) -> str:
        with open(qss_file_name, 'r', encoding='UTF-8') as file:
            return file.read()


if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)

    Windows = My_Windows()

    # 加载QSS
    Windows.setStyleSheet(QSSLoader.read_qss_file("img/style.qss"))

    if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
        Windows.info_message('系统托盘', '本系统不支持托盘功能')

    Windows.show()

    exit(app.exec_())


