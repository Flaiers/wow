from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep as wait
import pyscreenshot as ig
import pyautogui as pg
import cv2 as cv
import numpy as np
import threading
import requests
import keyboard
import design
import imutils
import time

headers = {
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.126 Yowser/2.5 Safari/537.36"
}
url = "https://www.дата-сегодня.рф/"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.started = False
        self.grid = []
        self.gridCheck = False
        self.ui = design.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.toggle)

    def toggle(self):
        print("Нажата кнопка")
        if not self.started:
            self.started = True
            self.gridSelected = False
            self.gridHotkey = self.ui.gridButton.keySequence().toString().lower() # Разметка области
            self.stopButton = self.ui.stopButton.keySequence().toString().lower() # кнопка остановки
            self.itemslot = self.ui.itemslot.value() # слот рыбалки
            self.key = self.ui.lineEdit.text() # ключ
            self.hitChance = self.ui.spinBox.value() # Шанс промаха
            self.mousemovetime = self.ui.spinBox_2.value() # Движение мыши

            if self.key == '':
                print("Ключ не введён")
                pg.alert("Ключ не введён, программа будет остановлена", "Приложение")
                self.started = False
                wait(1)
                self.ui.pushButton.setText("Старт")
                self.ui.pushButton.setStyleSheet("")
                print("Остановка")
                self

            else:
                req = requests.get(url, headers=headers)
                soup = BeautifulSoup(req.text, "lxml")
                now_full = soup.find("section", class_="main-glav").find("div", class_="container").find('p').text
                now = now_full.replace(" ", "")
                user_key = '-'.join(self.key)
                key_year = '202' + ''.join(user_key.split('-')[7])
                key_mounth = ''.join(user_key.split('-')[12:14])
                key_day = ''.join(user_key.split('-')[18:20])
                try:
                    data = datetime(int(now.split('.')[2]), int(now.split('.')[1]), int(now.split('.')[0]))
                    key_data = datetime(int(key_year), int(key_mounth), int(key_day))
                    period = data - key_data

                    # лицензия на 30 дней
                    if user_key.split('-')[0] == "3":
                        license =  30 - int(period.days)
                        if license > 0:
                            pg.alert(f'Осталось дней лицензии - {license}', "Приложение")
                            wait(0.2)
                            self.ui.pushButton.setText('Запускаю...')
                            self.ui.pushButton.setStyleSheet("background-color: rgb(38, 162, 105);color: white;")
                            threading.Thread(target=self.tracking).start()
                            threading.Thread(target=self.keyHandle).start()
                        elif license <= 0:
                            self.started = False
                            pg.alert('Время лицензии истекло', "Приложение")
                            wait(1)
                            self.ui.pushButton.setText("Старт")
                            self.ui.pushButton.setStyleSheet("background-color: rgb(38, 162, 105);color: white;")
                            print("Остановка")
                            self

                    # лицензия на 365 дней
                    elif user_key.split('-')[0] == "1":
                        license =  365 - int(period.days)
                        if license > 0:
                            pg.alert(f'Осталось дней лицензии - {license}', "Приложение")
                            wait(0.2)
                            self.ui.pushButton.setText('Запускаю...')
                            self.ui.pushButton.setStyleSheet("background-color: rgb(38, 162, 105);color: white;")
                            threading.Thread(target=self.tracking).start()
                            threading.Thread(target=self.keyHandle).start()
                        elif license <= 0:
                            self.started = False
                            pg.alert('Время лицензии истекло', "Приложение")
                            wait(1)
                            self.ui.pushButton.setText("Старт")
                            self.ui.pushButton.setStyleSheet("background-color: rgb(38, 162, 105);color: white;")
                            print("Остановка")
                            self

                    # лицензия на 90 дней
                    elif user_key.split('-')[-1] == "9":
                        license =  90 - int(period.days)
                        if license > 0:
                            pg.alert(f'Осталось дней лицензии - {license}', "Приложение")
                            wait(0.2)
                            self.ui.pushButton.setText('Запускаю...')
                            self.ui.pushButton.setStyleSheet("background-color: rgb(38, 162, 105);color: white;")
                            threading.Thread(target=self.tracking).start()
                            threading.Thread(target=self.keyHandle).start()
                        elif license <= 0:
                            self.started = False
                            pg.alert('Время лицензии истекло', "Приложение")
                            wait(1)
                            self.ui.pushButton.setText("Старт")
                            self.ui.pushButton.setStyleSheet("background-color: rgb(38, 162, 105);color: white;")
                            print("Остановка")
                            self

                except ValueError:
                    self.started = False
                    pg.alert('Ключ не правильный', "Приложение")
                    wait(1)
                    self.ui.pushButton.setText("Старт")
                    self.ui.pushButton.setStyleSheet("")
                    print("Остановка")
                    self

        elif self.started:
            self.started = False
            wait(1)
            self.ui.pushButton.setText("Старт")
            self.ui.pushButton.setStyleSheet("")
            print("Остановка")
            self

    def tracking(self):
        while self.started:
            needcrop = []
            if self.grid and self.started:
                print("Сетка есть")
                self.ui.pushButton.setText("Проверяю размеченную область...")
                self.ui.pushButton.setStyleSheet("background-color: green;color: white;")
                pg.press(str(self.itemslot))
                wait(3.3)
                im = self.getscreen()
                white = np.array(np.where(im == 255))
                if white.size:
                    self.ui.pushButton.setText("Жду пока поплавок всплывет")
                    found = True
                    w, h = pg.size()
                    firstpx = white[:,0]
                    lastpx = white[:,-1]
                    posx, posy = int(firstpx[1]+self.grid[0]), int(firstpx[0]+self.grid[1])
                    y,x,h,w = firstpx[0], firstpx[1], lastpx[0], lastpx[1]
                    while found and self.started:
                        wait(0.5)
                        img_canny = self.getscreen()
                        crop = img_canny[y:y+h, x:x+w] #  Обрезаем картинку до поплавка, чтобы было проще искать маркеры
                        cropsum = np.sum(crop == 255)
                        needcrop.append(cropsum)
                        print('Белые пиксели:', cropsum)
                        print('А нужно:', int(int(np.mean(needcrop))*1.15))
                        if cropsum >= int(int(np.mean(needcrop))*1.15):
                            pg.moveTo(posx, posy, self.mousemovetime)
                            # Сюда нужно вставить шанс промаха
                            pg.click(button='right')
                            needcrop.clear()
                            wait(4)
                            found = False
                        elif cropsum <= 10:
                            found = False
                            needcrop.clear()

                print("White:", white)
            elif not self.grid and self.started:
                self.ui.pushButton.setText("Ожидаю область видимости...")
                self.ui.pushButton.setStyleSheet("background-color: #e65100;color: white;")
            wait(0.5)

    def keyHandle(self):
        while self.started:
            if keyboard.is_pressed(self.gridHotkey):
                pg.alert("Разметьте мышкой область, в которой будет находится поплавок, затем нажмите Enter", "Приложение")
                wait(0.2)
                self.grid.clear()
                self.ui.pushButton.setText("ENTER - Подтвердить")
                shot = pg.screenshot()
                im = cv.cvtColor(np.array(shot), cv.COLOR_RGB2BGR)
                r = cv.selectROI("Screenshot", im, False)
                print(r)
                cv.destroyWindow("Screenshot")
                self.grid.append(r[0])
                self.grid.append(r[1])
                self.grid.append(r[2])
                self.grid.append(r[3])
            if keyboard.is_pressed(self.stopButton):
                self.toggle()

    def getscreen(self):
        im = ig.grab(backend="mss", childprocess=False, bbox=(self.grid[0], self.grid[1], self.grid[2]+self.grid[0], self.grid[3]+self.grid[1]))
        img_cv = cv.Canny(cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR), 80, 180)
        return img_cv

def main():
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec_()
    window.started = False

if __name__ == '__main__':
    main()
