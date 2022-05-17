from math import dist

from pyparsing import original_text_for
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


        # frame = camera_streamer.get_latest_frame()
        original_frame = camera_streamer.get_latest_frame()

        # TODO: add to config: draw rectangle around detection
        # TODO: return a list of face_detection_data and list of live_detection_data
        face_list, frame = face_rec.process_frame(original_frame)
        detection_list, frame = live_rec.process_frame(original_frame)

        # logging.info("Face detected -- {}".format(face_list))
        # logging.info("Live score -- {}".format(live_scores))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if face_list:
        #     logging.info('nobody')

        # else:
            # multiple faces detected
            for detection in detection_list:
                # TODO: draw if needed, see config
                cv2.rectangle(original_frame, (detection.startX, detection.startY), (detection.endX, detection.endY), (255, 255, 255), 2)
                logging.debug(f"Live detection COG: {detection.get_COG()}")

                
            for face in face_list:

                cv2.rectangle(original_frame, (face.left, face.top), (face.right, face.bottom), (0, 0, 0), 2)
                logging.debug(f"Face detection COG: {face.get_COG()}")
                        
                        
            print("--------------")
            print(dist(detection.get_COG(), face.get_COG()))
            print("--------------")

            if(dist(detection.get_COG(), face.get_COG()) < 1500):
                print(face.name, detection.score, detection.text)


            
                

        cv2.imshow('Video', original_frame)


if __name__ == '__main__':
    main()

