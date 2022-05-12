import logging
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import imutils
import pickle
import cv2
from pathlib import Path
import numpy as np
from camera_stream import CameraStream
import logging.config
from configparser import ConfigParser

# TODO:
# https://www.geeksforgeeks.org/difference-between-dataclass-vs-namedtuple-vs-object-in-python/
from collections import namedtuple
from live_detection_data import LiveDetectionData

# ap = argparse.ArgumentParser()
# ap.add_argument("-m", "--model", type=str, required=True,
#                 help="path to trained model")
# ap.add_argument("-l", "--label_encoder", type=str, required=True,
#                 help="path to label encoder")
# ap.add_argument("-d", "--detector", type=str, required=True,
#                 help="path to OpenCV's deep learning face detector")
# ap.add_argument("-c", "--confidence", type=float, default=0.5,
#                 help="minimum probability to filter weak detections")
# args = vars(ap.parse_args())

# USAGE
# python live_recognizer.py --model liveness.model --label_encoder label_encoder.pickle --detector face_detector_config


class LiveeeeRecognizer:
    def __init__(self, config):
        # TODO add config
        self.config = config

        #  TODO load values from config, ex paths
        logging.info("Loading face detector...")
        self.protoPath = "face_detector_config/deploy.prototxt"
        self.modelPath = "face_detector_config/res10_300x300_ssd_iter_140000.caffemodel"

        self.net = cv2.dnn.readNetFromCaffe(self.protoPath, self.modelPath)

        logging.info("Loading Model...")
        self.model = load_model("liveness.model")
        self.label_encoder = pickle.loads(open("le.pickle", "rb").read())

        self.confidence = 0.7

    def process_frame(self, frame):
        frame = imutils.resize(frame, width=600)
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))

        self.net.setInput(blob)
        detections = self.net.forward()

        detection_list = []

        # what does detection list contain??
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > self.confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)

                face = frame[startY:endY, startX:endX]
                face = cv2.resize(face, (32, 32))
                face = face.astype("float") / 255.0
                face = img_to_array(face)
                face = np.expand_dims(face, axis=0)

                predictions = self.model.predict(face)[0]
                j = np.argmax(predictions)
                # label = "{}: {:.4f}".format(self.label_encoder.classes_[j], predictions[j])
                # print(label)
                score = predictions[j]

                # logging.info(f"Live/Fake score -- {score}")

                # TODO only draw rectangle when enabled from config
                # TODO remove hard coded values
                if score > 0.60 and j == 1:
                    # if config.drawdetectiononframe:
                    # cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    # text_to_display = "Real: {:.4f}".format(score)
                    # cv2.putText(frame, text_to_display, (startX, startY - 10),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    logging.debug(f"Real: {score} : {j}")

                    detection_list.append(LiveDetectionData(score, 'real', startX, startY, endX, endY))

                else:
                    # cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                    # text_to_display = "Fake/Spoofed: {:.4f}".format(score)
                    # cv2.putText(frame, text_to_display, (startX, startY - 10),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    logging.debug(f"Fake: {score} : {j}")
                    detection_list.append(LiveDetectionData(score, 'fake', startX, startY, endX, endY))

                # cv2.putText(frame, label, (startX, startY - 10),
                #        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # cv2.rectangle(frame, (startX, startY), (endX, endY),
                #        (0, 0, 255), 2)

        # TODO should return detection+confidence, or only confident detections
        return detection_list, frame


def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    logging.config.fileConfig(Path("log_config.ini"))

    camera_streamer = CameraStream(config)
    camera_streamer.start()

    live_rec = LiveeeeRecognizer(config)

    while True:
        frame = camera_streamer.get_latest_frame()

        detection_list, frame = live_rec.process_frame(frame)
        for detection in detection_list:
            score, text, startX, startY, endX, endY = detection
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_streamer.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
