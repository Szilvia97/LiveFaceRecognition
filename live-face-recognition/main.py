from math import dist

from face_recognizer import FaceRecognizer
from live_recognizer import LiveeeeRecognizer
from camera_stream import CameraStream
import cv2
from pathlib import Path
from camera_stream import CameraStream
import logging.config
from configparser import ConfigParser


def main():
    # TODO add config
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    logging.config.fileConfig(Path("log_config.ini"))

    camera_streamer = CameraStream(config)
    camera_streamer.start()

    face_rec = FaceRecognizer(config)
    live_rec = LiveeeeRecognizer(config)

    while True:
            
        frame = camera_streamer.get_latest_frame()

        # TODO: add to config: draw rectangle around detection
        # TODO: return a list of face_detection_data and list of live_detection_data
        # TODO: make sure these list use the same coordinate system
        face_list = face_rec.process_frame(frame)
        live_list = live_rec.process_frame(frame)

        if face_list:
            for face in face_list:
                for detection in live_list:
                    face_cog = face.get_COG()
                    detection_cog = detection.get_COG()

                    # TODO: remove
                    logging.debug(f"Face: {face.get_COG()}, Live: {detection.get_COG()}, Dist = {dist(face.get_COG(), detection.get_COG())}")

                    # TODO: add correct number here
                    if dist(face_cog, detection_cog) < 100:
                        # TODO: draw if needed, see config
                        if True:
                            cv2.rectangle(frame, (face.left, face.top), (face.right, face.bottom), (0, 0, 0), 2)
                            cv2.putText(frame, face.name, (face.left + 6, face.bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                        (0, 0, 0), 1)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cv2.imshow('Video', frame)


if __name__ == '__main__':
    main()

