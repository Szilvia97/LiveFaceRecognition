import PySimpleGUI as psg
# from firebase import firebase
import logging.config
from configparser import ConfigParser
from pathlib import Path
from attendance import Attendance


class SimpleGui:
    selectable_size = (23, 1)
    button_size = (20, 1)
    font = ('Helvetica', 10)

    def __init__(self, config):
        self.config = config
        self.diplay_image_height = self.config.getint('DISPLAY_IMAGE_HEIGHT')
        self.diplay_image_width = self.config.getint('DISPLAY_IMAGE_WIDTH')

        self.attendance = Attendance(self.config)

        # firebase = firebase.FirebaseApplication('https://studentdatas-2ea41.firebaseio.com/', None)

        psg.theme('LightGreen3')

        self.button_start = self.config['BUTTON_START_LABEL']
        self.button_stop = self.config['BUTTON_STOP_LABEL']
        self.button_exit = self.config['BUTTON_EXIT_LABEL']

        # TODO: config with these
        self.course_list = ['Szoftverteszteles',
                            'OOP',
                            'Szoftverfejlesztes',
                            'Diszkret matematika',
                            'Kriptografia',
                            'Webtechnologiak']

        self.specialization_list = ['Szamitastechnika', 'Informatika', 'Tavkozles']

        self.room_list = ['114', '312', '230']

        self.week_list = ['het1', 'het2', 'het3', 'het4', 'het5']

        self.course_type_list = ['Eloadas', 'Labor']

        data_column = [
            [psg.Text('Válaszd ki a tárgyat')],
            [psg.Combo(self.course_list, size=self.selectable_size, key='subject')],
            [psg.Text('Válaszd ki az óra típusát')],
            [psg.Combo(self.course_type_list, size=self.selectable_size, key='type')],
            [psg.Text('Válaszd ki a szakot')],
            [psg.Combo(self.specialization_list, size=self.selectable_size, key='class')],
            [psg.Text('Válaszd ki a hetet')],
            [psg.Combo(self.week_list, size=self.selectable_size, key='week')],
            [psg.Text('Válaszd ki a termet')],
            [psg.Combo(self.room_list, size=self.selectable_size, key='classroom')],
            [psg.Button(self.button_start, size=self.button_size)],
            [psg.Button(self.button_stop, size=self.button_size)],
            [psg.Button(self.button_exit, size=self.button_size)]
        ]

        self.layout = [
            [
                psg.Image(key='image_box', size=(self.diplay_image_height, self.diplay_image_width)),
                psg.Column(data_column),
            ]
        ]

        self.window = psg.Window('Attendance monitor', self.layout, font=self.font)

    def run(self):
        while True:
            frame_bytes, lista = self.attendance.get_latest_frame(resized_bytes=True)

            print(lista)

            # Timeout = milliseconds to wait until the Read will return
            event, values = self.window.read(timeout=10)

            if event == self.button_exit or event == psg.WIN_CLOSED:
                break

            if event == self.button_start:
                self.attendance.start()

            if event == self.button_stop:
                # TODO: start improc and start camera use separately?
                pass

            self.window["image_box"].update(data=frame_bytes)

        self.window.close()
        self.attendance.stop()


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

    logging.config.fileConfig(Path("log_config.ini"))

    display = SimpleGui(config)
    display.run()


if __name__ == '__main__':
    main()
