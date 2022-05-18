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

        # do the magic
    while True:
            # # forditva gondolkozni:
            # # run liveness -> list of live fejek -> csak erre hivni a recognizeot
            # # live = [(rectangle, 0.7), (rectangle, 0.4), (rectangle, 0.7)]
            # # a recognize, csak 0.6nal nagyobb rectanglebe kell keressen

        frame = camera_streamer.get_latest_frame()

        # TODO: add to config: draw rectangle around detection
        # TODO: return a list of face_detection_data and list of live_detection_data
        # TODO: make sure these list use the same coordinate system
        face_list = face_rec.process_frame(frame)
        live_list = live_rec.process_frame(frame)

        # logging.info("Face detected -- {}".format(face_list))
        # logging.info("Live score -- {}".format(live_scores))cv2.rectangle(frame, (detection.startX, detection.startY), (detection.endX, detection.endY), (255, 255, 255), 2)

        if face_list:
            for face in face_list:
                # logging.debug(f"Face detection COG: {face.get_COG()}")

                for detection in live_list:
                    face_cog = face.get_COG()
                    detection_cog = detection.get_COG()

                    # TODO: remove
                    logging.debug(f"Face: {face.get_COG()}, Live: {detection.get_COG()}, Dist = {dist(face.get_COG(), detection.get_COG())}")

                    # TODO: add correct number here
                    if dist(face_cog, detection_cog) < 100:
                        # TODO: draw if needed, see config
                        # logging.debug(f"Live detection COG: {detection.get_COG()}")

                        if True:
                            cv2.rectangle(frame, (face.left, face.top), (face.right, face.bottom), (0, 0, 0), 2)
                            cv2.putText(frame, face.name, (face.left + 6, face.bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                                        (0, 0, 0), 1)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # frame = cv2.resize(frame, (800, 600))
        # cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.imshow('Video', frame)


if __name__ == '__main__':
    main()

