import PySimpleGUI as psg
import logging.config
from configparser import ConfigParser
from pathlib import Path
import cv2
from camera_stream import CameraStream

class RegisterGui:
    selectable_size = (23, 1)
    button_size = (20, 1)
    font = ('Helvetica', 10)

    def __init__(self, config):
        self.config = config
        self.diplay_image_height = self.config.getint('DISPLAY_IMAGE_HEIGHT')
        self.diplay_image_width = self.config.getint('DISPLAY_IMAGE_WIDTH')

        psg.theme('LightGreen3')

        self.camera_streamer = CameraStream(config)

        self.button_exit = self.config['BUTTON_EXIT_LABEL']
        self.button_save = self.config['BUTTON_SAVE_LABEL']

        self.specialization_list = [
            'Szamitastechnika', 'Informatika', 'Tavkozles']

        self.student_data_column = [
            [psg.Text('Szak:')],
            [psg.Combo(self.specialization_list, size=self.selectable_size, key='class')],
            [psg.Text('Teljes név:')],
            [psg.Input(key='name', size=self.selectable_size, enable_events=True)],
            [psg.Text('Neptun azonosító:')],
            [psg.Input(key='neptun_id', size=self.selectable_size, enable_events=True)],
            [psg.Text(size=(25, 1), k='-OUTPUT-')],
            [psg.Button(self.button_exit, size=self.button_size)],
            [psg.Button(self.button_save, size=self.button_size)],
        ]
        
        self.layout = [
            [psg.Image(key='camera_box', size=(
                self.diplay_image_height, self.diplay_image_width)),
             psg.Column(self.student_data_column),
            ]
        ]

        self.window = psg.Window('Diák mentése', self.layout, finalize=True, modal=True)


    def run(self):

        self.camera_streamer.start()

        while True:

            frame = self.camera_streamer.get_latest_frame()
            frame_bytes = self.camera_streamer.resize_frame_to_bytes(frame, self.diplay_image_width, self.diplay_image_height)
            
            event, values = self.window.read(timeout=10)

            if event == self.button_exit or event == psg.WIN_CLOSED:
                break

            if event == self.button_save:
                if values['class'] != "" and values['name'] != "" and values['neptun_id'] != "":
                    cv2.imwrite('recognize-images/' + values['neptun_id'] + "_" + values['name'] + "_" + values['class'] + '.png', frame)
                    psg.popup('OK', 'Diák mentve!')
                else:
                    psg.popup('Hiba', 'Minden mező kitöltése kötelező!')

            self.window["camera_box"].update(data=frame_bytes)

        self.window.close()
        self.camera_streamer.stop()

def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    logging.config.fileConfig(Path("log_config.ini"))

    display = RegisterGui(config)
    display.run()


if __name__ == '__main__':
    main()
