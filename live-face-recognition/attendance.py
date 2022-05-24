from math import dist
import numpy as np
from face_recognizer import FaceRecognizer
from live_recognizer import LiveeeeRecognizer
from camera_stream import CameraStream
import cv2
from pathlib import Path
from camera_stream import CameraStream
import logging.config
from configparser import ConfigParser
import threading


class Attendance:
    def __init__(self, config):
        self.config = config

        self.camera_streamer = CameraStream(config)

        self.face_rec = FaceRecognizer(config)
        self.live_rec = LiveeeeRecognizer(config)

        self.started = False
        self.thread = threading.Thread(target=self.update, name='WorkerThread', args=())
        self.read_lock = threading.Lock()

        self.height = self.config.getint('CAMERA_HEIGHT')
        self.width = self.config.getint('CAMERA_WIDTH')
        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

        self.face_list = []
        self.live_list = []

    def start(self):
        if self.started:
            return

        self.camera_streamer.start()

        self.started = True
        self.thread.start()

    def stop(self):
        if self.started:
            self.started = False

            self.camera_streamer.stop()

            self.thread.join()

    def update(self):
        logging.info('Start')

        while self.started:
            frame = self.camera_streamer.get_latest_frame()

            # TODO: thread pool, this could be done in parallel
            # self.face_list = self.face_rec.process_frame(frame)
            # self.live_list = self.live_rec.process_frame(frame)
            #
            # if self.face_list:
            #     for face in self.face_list:
            #         for detection in self.live_list:
            #             face_cog = face.get_COG()
            #             detection_cog = detection.get_COG()
            #
            #             # TODO: remove
            #             logging.debug(
            #                 f"Face: {face.get_COG()}, Live: {detection.get_COG()}, Dist = {dist(face.get_COG(), detection.get_COG())}")
            #
            #             # TODO: add correct number here
            #             if dist(face_cog, detection_cog) < 100:
            #                 # TODO: draw if needed, see config
            #                 if True:
            #                     cv2.rectangle(frame, (face.left, face.top), (face.right, face.bottom), (0, 255, 0), 2)
            #                     cv2.putText(frame, face.name + " - " + detection.text, (face.left + 6, face.bottom - 6),
            #                                 cv2.FONT_HERSHEY_DUPLEX, 0.6,
            #                                 (255, 0, 255), 1)

            self.read_lock.acquire()
            self.frame = frame
            self.read_lock.release()

    def get_latest_frame(self) -> np.array:
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

def main():
    # TODO add config
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    # logging.config.fileConfig(Path("log_config.ini"))

    attendance = Attendance(config)
    attendance.start()

    while True:
        frame = attendance.get_latest_frame()
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    attendance.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
