import PySimpleGUI as psg
# from firebase import firebase
from datetime import datetime
import logging.config
from configparser import ConfigParser
from pathlib import Path
from attendance import Attendance
import threading
import cv2
import time
import numpy as np


class SimpleGui:
    def __init__(self, config):
        self.config = config
        self.height = self.config.getint('CAMERA_HEIGHT')
        self.width = self.config.getint('CAMERA_WIDTH')
        self.fps = self.config.getint('CAMERA_FPS')
        self.attendance = Attendance(self.config)

        # Prepare a blank image
        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

        # firebase = firebase.FirebaseApplication('https://studentdatas-2ea41.firebaseio.com/', None)

        psg.theme('LightGreen3')

        self.button_start_name = 'Kezdés'

        # self.layout = [
        #     [psg.Image(filename='', key='image_box', size=(self.height, self.width))],
        #     [psg.Button(self.button_start_name, size=(10, 1), font='Helvetica 14')]
        # ]

        self.layout = [
            [psg.Text('Válaszd ki a tárgyat', size=(100, 1), font='Lucida', justification='left')],
            [psg.Combo(['Szoftverteszteles', 'OOP', 'Szoftverfejlesztes', 'Diszkret matematika', 'Kriptografia','Webtechnologiak'], key='subject')],
            [psg.Text('Válaszd ki az óra típusát ', size=(30, 1), font='Lucida', justification='left')],
            [psg.Combo(['Eloadas', 'Labor'], key='type')],
            [psg.Text('Válaszd ki a szakot ', size=(30, 1), font='Lucida', justification='left')],
            [psg.Combo(['Szamitastechnika', 'Informatika', 'Tavkozles'], key='class')],
            [psg.Text('Válaszd ki a hetet ', size=(30, 1), font='Lucida', justification='left')],
            [psg.Combo(['het1', 'het2', 'het3', 'het4', 'het5'], key='week')],
            [psg.Text('Válaszd ki a termet ', size=(30, 1), font='Lucida', justification='left')],
            [psg.Combo(['114', '312', '230'], key='classroom')],
            [psg.Image(filename='', key='image_box', size=(self.height, self.width))],
            [psg.Button('Kezdes', font=('Times New Roman', 12), size=(10, 1)),
            psg.Button('Leállítás', font=('Times New Roman', 12), size=(10, 1))]
            ]

        # self.window = psg.Window('Jelenlét', self.layout, size=(360, 360), auto_size_buttons=True, auto_size_text=True, resizable=True,
        #             finalize=True)
        self.window = psg.Window('PySimpleGUI', self.layout, location=(200, 200))

        self.previous_time = time.perf_counter()

        self.started = False
        self.thread = threading.Thread(target=self.update, name='WorkerThread', args=())

    def start(self):
        if self.started:
            return

        self.attendance.start()
        self.started = True
        self.thread.start()

    def stop(self):
        if self.started:
            self.started = False

            self.attendance.stop()
            self.thread.join()

    def update(self):
        while self.started:
            frame = self.attendance.get_latest_frame()

            # Timeout = milliseconds to wait until the Read will return
            event, values = self.window.read(timeout=10)

            if event == self.button_start_name or event == psg.WIN_CLOSED:
                self.started = False
                break

            current_time = time.perf_counter()
            elapsed_time = current_time - self.previous_time
            self.previous_time = current_time

            if elapsed_time > 0:
                fps_text = f"FPS: {self.fps} / {1 / elapsed_time:.2f}"
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, fps_text, (10, 20), font, 0.4, (255, 255, 255), 1)

            img_bytes = cv2.imencode(".png", frame)[1].tobytes()
            self.window["image_box"].update(data=img_bytes)

        self.window.close()

# while True:
#     event, values = window.read()
#     if event in ('Leállítás', None):
#         break
#     if event == self.button_start_name:
#         # attendance.start()
#         # win.close()
#         now = datetime.now()
#         date_string = now.strftime("%Y-%m-%d")
#         time_string = now.strftime("%H:%M:%S")
#
#         studentData = {'deviceId': '',
#                        'isAttendanceRecovery': '',
#                        'neptunId': '',
#                        'profile': '',
#                        'studentName': ''
#                        }
#
#         subject = values['subject']
#         type = values['type']
#         className = values['class']
#         week = values['week']
#         classroom = values['classroom']
#
#         # result = firebase.patch(
#         #     'Jelenlet/' + subject + '/' + type + '/' + className + '/' + week + '/' + classroom + '/' + date_string + '/' + time_string,
#         #     studentData)
#         # print(result)
#
#         # psg.popup('Az óra adatai',
#         # 'Az óra neve: '+ values['subject'] + '\nTípusa: '+ values['type'] +' \nIdőpont: ' + classTime[1:len(classTime)-1] +' \nSzak: ' + values['class'])
#
#     # elif event == 'Download':


def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    display = SimpleGui(config)
    display.start()

    while True:
        pass

    display.stop()


if __name__ == '__main__':
    main()
