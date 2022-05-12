
import face_recognition
import cv2
from pathlib import Path
import numpy as np
import os
from camera_stream import CameraStream
import logging.config
from configparser import ConfigParser


class FaceRecognizer:
    def __init__(self, config):
        self.config = config

        # TODO better way of storing these: name, image, face_encoding
        self.known_face_encodings = []
        self.known_face_names = []

        # TODO path from config
        # TODO load these somehow
        for file in Path("recognize-images").glob('*.png'):
            image = face_recognition.load_image_file(file)
            face_encoding = face_recognition.face_encodings(image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(file.stem)

    def process_frame(self, frame):
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]
        # print(rgb_small_frame)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        # TODO only draw rectangle when enabled from config
        # for (top, right, bottom, left), name in zip(face_locations, face_names):
        #     top *= 4
        #     right *= 4
        #     bottom *= 4
        #     left *= 4
        #     cv2.rectangle(frame, (left, top), (right, bottom), (255,0,255), 2)
        #     cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255,0,255), cv2.FILLED)
        #     font = cv2.FONT_HERSHEY_DUPLEX
        #     cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (0,0,0), 1)

        return face_names, frame


def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    logging.config.fileConfig(Path("log_config.ini"))

    camera_streamer = CameraStream(config)
    camera_streamer.start()

    face_rec = FaceRecognizer(config)

    while True:
        frame = camera_streamer.get_latest_frame()

        face_names, frame = face_rec.process_frame(frame)

        logging.info("Face detected -- {}".format(face_names))

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_streamer.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
