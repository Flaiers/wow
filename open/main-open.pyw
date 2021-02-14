from PyQt5 import QtCore, QtGui, QtWidgets
from time import sleep as wait
import pyscreenshot as ig
import pyautogui as pg
import cv2 as cv
import numpy as np
import threading
import keyboard
import imutils
import design

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
            self.hitChance = self.ui.spinBox.value() # Шанс промаха
            self.mousemovetime = self.ui.spinBox_2.value() # Движение мыши
            print("Запуск")
            self.ui.pushButton.setText("Запускаю...")
            self.ui.pushButton.setStyleSheet("background-color: rgb(38, 162, 105);color: white;")
            threading.Thread(target=self.tracking).start()
            threading.Thread(target=self.keyHandle).start()
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
