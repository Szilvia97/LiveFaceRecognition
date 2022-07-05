import logging
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import cv2
from pathlib import Path
import numpy as np
from camera_stream import CameraStream
import logging.config
from configparser import ConfigParser
from live_detection_data import LiveDetectionData


class MyLiveRecognizer:
    def __init__(self, config):
        self.config = config
        self.min_live_score = self.config.getfloat('MIN_LIVE_SCORE')
        self.is_live = self.config.getint('IS_LIVE')

        logging.info("Loading face detector...")
        self.protoPath = "face_detector_config/deploy.prototxt"
        self.modelPath = "face_detector_config/res10_300x300_ssd_iter_140000.caffemodel"

        self.net = cv2.dnn.readNetFromCaffe(self.protoPath, self.modelPath)

        logging.info("Loading Model...")
        self.model = load_model("liveness.model")

        self.confidence = 0.7

    def live_detection_process(self, image):
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)),
                                     1.0,
                                     (300, 300),
                                     (104.0, 177.0, 123.0))

        self.net.setInput(blob)
        detections = self.net.forward()

        detection_list = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > self.confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype('int')

                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)

                try:
                    face = image[startY:endY, startX:endX]
                    face = cv2.resize(face, (32, 32))
                    face = face.astype('float') / 255.0
                    face = img_to_array(face)
                    face = np.expand_dims(face, axis=0)
            
                    predictions = self.model.predict(face)[0]
                    max_index = np.argmax(predictions)
                    score = predictions[max_index]

                    if score > self.min_live_score and max_index == self.is_live:
                        detection_list.append(LiveDetectionData(
                            score, 'real', startX, startY, endX, endY))
                    else:
                        detection_list.append(LiveDetectionData(
                            score, 'fake', startX, startY, endX, endY))

                except Exception as e:
                    print(str(e))

        return detection_list


def main():
    config_object = ConfigParser()
    config_object.read(Path("config.ini"))
    config = config_object["DEFAULT"]

    camera_streamer = CameraStream(config)
    camera_streamer.start()

    live_rec = MyLiveRecognizer(config)

    while True:
        frame = camera_streamer.get_latest_frame()

        detection_list = live_rec.process_frame(frame)

        for detection in detection_list:
            cv2.rectangle(frame, (detection.startX, detection.startY),
                          (detection.endX, detection.endY), (255, 255, 255), 2)
            cv2.putText(frame, detection.text, (detection.startX, detection.startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        frame = cv2.resize(frame, (800, 600))

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_streamer.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
