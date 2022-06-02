import datetime
import PySimpleGUI as psg
import logging.config
from configparser import ConfigParser
from pathlib import Path
from attendance import Attendance
from session_data import SessionData
import cv2

from ui_register import RegisterGui


class SimpleGui:
    selectable_size = (23, 1)
    button_size = (20, 1)
    font = ('Helvetica', 10)

    def __init__(self, config):
        self.config = config
        self.diplay_image_height = self.config.getint('DISPLAY_IMAGE_HEIGHT')
        self.diplay_image_width = self.config.getint('DISPLAY_IMAGE_WIDTH')

        self.attendance = Attendance(self.config)


        psg.theme('LightGreen3')

        self.button_start = self.config['BUTTON_START_LABEL']
        self.button_stop = self.config['BUTTON_STOP_LABEL']
        self.button_exit = self.config['BUTTON_EXIT_LABEL']
        self.button_photo = self.config['BUTTON_PHOTO_LABEL']

        self.select_course_label = self.config['SELECT_COURSE_LABEL']
        self.select_course_type_label = self.config['SELECT_COURSE_TYPE_LABEL']
        self.select_room_label = self.config['SELECT_ROOM_LABEL']
        self.select_week_label = self.config['SELECT_WEEK_LABEL']
        self.select_specialization_label = self.config['SELECT_SPECIALIZATION_LABEL']

        self.course_list = self.config['COURSE_LIST'].split(',')

        self.specialization_list = self.config['SPECIALIZATION_LIST'].split(',')

        self.room_list = self.config['ROOM_LIST'].split(',')

        self.week_list = self.config['WEEK_LIST'].split(',')

        self.course_type_list = self.config['COURSE_TYPE_LIST'].split(',')

        data_column = [
            [psg.Text(self.select_course_label)],
            [psg.Combo(self.course_list, size=self.selectable_size, key='subject')],
            [psg.Text(self.select_course_type_label)],
            [psg.Combo(self.course_type_list,
                       size=self.selectable_size, key='type')],
            [psg.Text(self.select_specialization_label)],
            [psg.Combo(self.specialization_list,
                       size=self.selectable_size, key='class')],
            [psg.Text(self.select_week_label)],
            [psg.Combo(self.week_list, size=self.selectable_size, key='week')],
            [psg.Text(self.select_room_label)],
            [psg.Combo(self.room_list, size=self.selectable_size, key='classroom')],
            [psg.Text(size=(25, 1), k='-OUTPUT-')],
            [psg.Button(self.button_start, size=self.button_size)],
            [psg.Button(self.button_stop, size=self.button_size)],
            [psg.Button(self.button_exit, size=self.button_size)],
            [psg.Button(self.button_photo, size=self.button_size)],
        ]


        self.layout = [
            [
                psg.Image(key='image_box', size=(
                    self.diplay_image_height, self.diplay_image_width)),
                psg.Column(data_column),
            ]
        ]

        
        self.window = psg.Window('Attendance monitor',
                                 self.layout, font=self.font)

    

    def run(self):
        while True:
            frame_bytes = self.attendance.get_latest_frame(resized_bytes=True)

            event, values = self.window.read(timeout=10)

            if event == self.button_exit or event == psg.WIN_CLOSED:
                break

            if event == self.button_photo:
                register_gui = RegisterGui(self.config)
                register_gui.run()

            if event == self.button_start:

                if values['subject'] != "" and values['type'] != "" and values['class'] != "" and values['week'] != "" and values['classroom'] != "":
                    psg.popup('OK', 'Az adatok mentése elkezdődik!')

                    session_data = SessionData(subject=values['subject'],
                                               type=values['type'],
                                               className=values['class'],
                                               week=values['week'],
                                               classroom=values['classroom'],
                                               date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                               time=datetime.datetime.now().strftime("%H:%M:%S"))
                    self.attendance.start(session_data)
                else:
                    psg.popup('Hiba', 'Minden mező kitöltése kötelező!')

            if event == self.button_stop:
                self.attendance.stop()
                pass

            self.window["image_box"].update(data=frame_bytes)

        self.window.close()
        self.attendance.stop()




def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    logging.config.fileConfig(Path("log_config.ini"))

    display = SimpleGui(config)
    display.run()


if __name__ == '__main__':
    main()
