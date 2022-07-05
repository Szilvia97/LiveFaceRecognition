from math import dist
import numpy as np
from face_recognizer import FaceRecognizer
from live_recognizer import MyLiveRecognizer
import cv2
from pathlib import Path
from camera_stream import CameraStream
import logging.config
from configparser import ConfigParser
import threading
import time
from firebase import firebase
from session_data import SessionData


class Attendance:
    def __init__(self, config):
        self.config = config

        self.camera_streamer = CameraStream(config)

        self.face_rec = FaceRecognizer(config)
        self.live_rec = MyLiveRecognizer(config)

        self.started = False
        self.thread = threading.Thread(
            target=self.update, name='AttendanceThread', args=())
        self.read_lock = threading.Lock()

        self.height = self.config.getint('CAMERA_HEIGHT')
        self.width = self.config.getint('CAMERA_WIDTH')
        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

        self.diplay_image_height = self.config.getint('DISPLAY_IMAGE_HEIGHT')
        self.diplay_image_width = self.config.getint('DISPLAY_IMAGE_WIDTH')

        self.show_fps = config.getboolean('CAMERA_SHOW_FPS')
        self.previous_time = time.perf_counter()

        self.db = firebase.FirebaseApplication('https://studentdatas-2ea41.firebaseio.com/', None)

        self.face_list = []
        self.live_list = []
        self.identified_student_list = []

    def start(self, session_data: SessionData):
        if self.started:
            return

        self.session_data = session_data
        self.identified_student_list.clear()

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

            self.face_list = self.face_rec.face_recognition_process(frame)
            self.live_list = self.live_rec.live_detection_process(frame)

            if self.face_list:
                for face in self.face_list:
                    for detection in self.live_list:
                        face_cog = face.get_COG()
                        detection_cog = detection.get_COG()

                        if dist(face_cog, detection_cog) < 100:
                            items = face.name.split('_')

                            if not items:
                                return
                            
                            if face.name not in self.identified_student_list and detection.text == 'real' and face.name != 'Unknown':
                                self.identified_student_list.append(face.name)

                                studentData = {'isAttendanceRecovery': False,
                                               'neptunId': items[0],
                                               'studentName': items[1],
                                               'profile': items[2]
                                               }

                                print(self.session_data)

                                result = self.db.patch('Jelenlet/' + self.session_data.subject + '/' + self.session_data.type + '/' + self.session_data.className + '/' +
                                                        self.session_data.week + '/' + self.session_data.classroom + '/' +
                                                        self.session_data.date + '/' + self.session_data.time + '/' + items[0],
                                                        studentData)
                                print(result)


                            if detection.text == 'fake' or items[0] == 'Unknown':
                                cv2.rectangle(
                                    frame, (face.left, face.top), (face.right, face.bottom), (0, 0, 255), 2)
                                cv2.putText(frame, items[0] + " - " + detection.text, (face.left + 6, face.bottom - 6),
                                            cv2.FONT_HERSHEY_DUPLEX, 1.0,
                                            (255, 255, 255), 1)

                            else:
                                cv2.rectangle(
                                    frame, (face.left, face.top), (face.right, face.bottom), (0, 255, 0), 2)
                                cv2.putText(frame, items[1] + " - " + detection.text, (face.left + 6, face.bottom - 6),
                                            cv2.FONT_HERSHEY_DUPLEX, 1.0,
                                            (255, 255, 255), 1)

                            

                            

            self.read_lock.acquire()
            self.frame = frame
            self.read_lock.release()

        logging.info('Stop')

    def get_latest_frame(self, resized_bytes=True):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()

        if resized_bytes:
            frame = cv2.resize(
                frame, (self.diplay_image_height, self.diplay_image_width))
            frame_bytes = cv2.imencode(".png", frame)[1].tobytes()
            return frame_bytes

        return frame

    def get_identified_student_list(self):
        self.read_lock.acquire()
        identified_student_list = self.identified_student_list.copy()
        self.read_lock.release()

        return identified_student_list


def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    logging.config.fileConfig(Path("log_config.ini"))

    attendance = Attendance(config)
    attendance.start(session_data=SessionData)

    while True:
        frame = attendance.get_latest_frame(resized_bytes=False)
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    attendance.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
