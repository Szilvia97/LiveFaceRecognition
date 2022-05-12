# from cProfile import label
# from gevent import config
from face_recognizer import FaceRecognizer
from live_recognizer import LiveeeeRecognizer
from camera_stream import CameraStream
import cv2
from pathlib import Path
import numpy as np
import os
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
        face_names, frame = face_rec.process_frame(frame)
        detection_list, frame = live_rec.process_frame(frame)

        logging.info("Face detected -- {}".format(face_names))
        # logging.info("Live score -- {}".format(live_scores))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if len(face_names) == 0:
            logging.info('nobody')

        else:
            # multiple faces detected
            for detection in detection_list:
                # TODO: draw if needed, see config
                cv2.rectangle(frame, (detection.startX, detection.startY), (detection.endX, detection.endY), (0, 0, 255), 2)
                logging.debug(f"COG: {detection.get_COG()}")
            # TODO: find COGs that are closest

        cv2.imshow('Video', frame)


if __name__ == '__main__':
    main()

