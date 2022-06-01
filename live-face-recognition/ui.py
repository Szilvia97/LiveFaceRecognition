import datetime
import PySimpleGUI as psg
import logging.config
from configparser import ConfigParser
from pathlib import Path
from attendance import Attendance
from session_data import SessionData
import cv2


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

        # TODO: config with these
        self.course_list = ['Szoftverteszteles',
                            'Szoftverfejlesztes',
                            'Diszkret matematika',
                            'Kriptografia',
                            'Webtechnologiak']

        self.specialization_list = [
            'Szamitastechnika', 'Informatika', 'Tavkozles']

        self.room_list = ['114', '312', '230']

        self.week_list = ['het1', 'het2', 'het3', 'het4', 'het5']

        self.course_type_list = ['Eloadas', 'Labor']

        data_column = [
            [psg.Text('Válaszd ki a tárgyat')],
            [psg.Combo(self.course_list, size=self.selectable_size, key='subject')],
            [psg.Text('Válaszd ki az óra típusát')],
            [psg.Combo(self.course_type_list,
                       size=self.selectable_size, key='type')],
            [psg.Text('Válaszd ki a szakot')],
            [psg.Combo(self.specialization_list,
                       size=self.selectable_size, key='class')],
            [psg.Text('Válaszd ki a hetet')],
            [psg.Combo(self.week_list, size=self.selectable_size, key='week')],
            [psg.Text('Válaszd ki a termet')],
            [psg.Combo(self.room_list, size=self.selectable_size, key='classroom')],
            [psg.Button(self.button_start, size=self.button_size)],
            [psg.Button(self.button_stop, size=self.button_size)],
            [psg.Button(self.button_exit, size=self.button_size)],
            [psg.Button(self.button_photo, size=self.button_size)],
        ]

        self.student_data_column = [
            [psg.Text('Szak:')],
            [psg.Combo(self.specialization_list,
                   size=self.selectable_size, key='class')],
            [psg.Text('Teljes név:')],
            [psg.Input(key='name', enable_events=True)],
            [psg.Text('Neptun azonosító:')],
            [psg.Input(key='neptun_id', enable_events=True)],
            [psg.Text(size=(25, 1), k='-OUTPUT-')],
            [psg.Button(self.button_exit, size=self.button_size)],
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

        # self.input_key_list = [key for key, value in self.window.key_dict.items()
        #     if isinstance(value, psg.Input)]
    def make_photo(self):
        camera = cv2.VideoCapture(0)
        while True:
            return_value, image = camera.read()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cv2.imshow('image', gray)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.imwrite('recognize-images/test.jpg', image)
                break
        camera.release()
        cv2.destroyAllWindows()

    def add_photos_window(self):
        self.layout = [
            [psg.Image(key='image_box', size=(
                self.diplay_image_height, self.diplay_image_width)),
             psg.Column(self.student_data_column),
            ]
        ]
        return psg.Window('Save pictures of students', self.layout, finalize=True)

    def run(self):
        while True:
            frame_bytes = self.attendance.get_latest_frame(resized_bytes=True)

            # Timeout = milliseconds to wait until the Read will return
            event, values = self.window.read(timeout=10)

            if event == self.button_exit or event == psg.WIN_CLOSED:
                break

            if event == self.button_photo:
                self.add_photos_window()
                # self.make_photo()

            if event == self.button_start:

                # if all(map(str.strip, [values[key] for key in self.input_key_list])):
                if values['subject'] != "" and values['type'] != "" and values['class'] != "" and values['week'] != "" and values['classroom'] != "":
                    # ptoaster.notify('OK', 'All inputs are OK!')
                    psg.popup('OK', 'Az adatok mentése elkezdődött!')

                    session_data = SessionData(subject=values['subject'],
                                               type=values['type'],
                                               className=values['class'],
                                               week=values['week'],
                                               classroom=values['classroom'],
                                               date=datetime.datetime.now().strftime("%Y-%m-%d"),
                                               time=datetime.datetime.now().strftime("%H:%M:%S"))
                    self.attendance.start(session_data)
                else:
                    # ptoaster.notify('Ups..', 'Some inputs missed!')
                    psg.popup('Hiba', 'Minden mező kitöltése kötelező!')

            if event == self.button_stop:
                # TODO: start improc and start camera use separately?
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
