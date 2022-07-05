import face_recognition
import cv2
from pathlib import Path
import numpy as np
import os
from camera_stream import CameraStream
import logging.config
from configparser import ConfigParser
import time

from face_detection_data import FaceDetectionData


class FaceRecognizer:
    def __init__(self, config):
        self.config = config
        self.known_face_encodings = []
        self.known_face_names = []

        for file in Path("student-recognize-images").glob('*.png'):
            image = face_recognition.load_image_file(file)
            face_encoding = face_recognition.face_encodings(image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(file.stem)

    # def process_frame(self, image, scaling_factor=4):
    #     face_names, face_list = [], []

    #     image = cv2.resize(image, (0, 0), fx=1.0 /
    #                        scaling_factor, fy=1.0/scaling_factor)
    #     rgb_image = image[:, :, ::-1]

    #     face_locations = face_recognition.face_locations(rgb_image)
    #     face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    #     for face_encoding in face_encodings:
    #         matches = face_recognition.compare_faces(
    #             self.known_face_encodings, face_encoding, tolerance=0.6)
    #         face_distances = face_recognition.face_distance(
    #             self.known_face_encodings, face_encoding)
    #         best_match_index = np.argmin(face_distances)

    #         name = self.known_face_names[best_match_index] if matches[best_match_index] else "Unknown"
    #         face_names.append(name)

    #     for (top, right, bottom, left), name in zip(face_locations, face_names):
    #         top *= scaling_factor
    #         right *= scaling_factor
    #         bottom *= scaling_factor
    #         left *= scaling_factor

    #         face_list.append(FaceDetectionData(name, left, top, right, bottom))

    #     return face_list

    def process_frame(self, frame):
        face_locations = []
        face_encodings = []
        face_names = []

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        face_list = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            face_list.append(FaceDetectionData(name=name, left=left, top=top, right=right, bottom=bottom))

        return face_list


def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]
    camera_streamer = CameraStream(config)
    camera_streamer.start()

    face_rec = FaceRecognizer(config)

    while True:
        frame = camera_streamer.get_latest_frame()

        face_list = face_rec.process_frame(frame)

        for face in face_list:
            cv2.rectangle(frame, (face.left, face.top),
                          (face.right, face.bottom), (0, 0, 0), 2)
            cv2.putText(frame, face.name, (face.left + 6, face.bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 0), 1)

        frame = cv2.resize(frame, (800, 600))
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_streamer.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
