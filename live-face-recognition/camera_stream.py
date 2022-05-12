import logging.config
from configparser import ConfigParser
from pathlib import Path
import numpy as np
import threading
import cv2


class CameraStream:
    def __init__(self, config):
        self.config = config

        self.height = self.config.getint('CAMERA_HEIGHT')
        self.width = self.config.getint('CAMERA_WIDTH')
        self.fps = self.config.getint('CAMERA_FPS')

        # Prepare a blank image
        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

        self.streamId = config.getint('CAMERA_ID')
        self.stream = cv2.VideoCapture(self.streamId)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.stream.set(cv2.CAP_PROP_FPS, self.fps)

        self.img = cv2.imread('1.jpg')
        if not self.stream.isOpened():
            logging.info(f'Failed to open camera: {self.streamId}')
            exit(1)

        self.started = False
        self.thread = threading.Thread(target=self.update, name='WorkerThread', args=())
        self.read_lock = threading.Lock()

    def get_latest_frame(self) -> np.array:
        self.read_lock.acquire()
        # frame = self.frame.copy()
        frame = self.img
        self.read_lock.release()
        return frame

    def start(self):
        if self.started:
            return

        self.started = True
        self.thread.start()

    def stop(self):
        if self.started:
            self.started = False

            self.thread.join()

            self.stream.release()

    def update(self):
        logging.info('Start')

        while self.started:
            ret, frame = self.stream.read()

            if not ret:
                logging.info('Cannot grab frame')
                exit(2)

            self.read_lock.acquire()
            self.frame = frame
            self.read_lock.release()

        logging.info('Stop')


def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    logging.config.fileConfig(Path("log_config.ini"))

    camera_streamer = CameraStream(config)
    camera_streamer.start()

    while True:
        frame = camera_streamer.get_latest_frame()
        cv2.imshow('Camera stream', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_streamer.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
