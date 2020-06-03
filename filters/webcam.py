import cv2
import filters
import numpy as np


class Webcam:
    @classmethod
    def config(cls):
        return {
            "Device": {"type": "device"}
        }

    def __init__(self, device, *args, **kwargs):
        config = kwargs['config']
        self.cap = cv2.VideoCapture(device)

    def apply(self, *args, **kwargs):
        frame = kwargs['frame']
        shape = frame.shape

        success, webcam_frame = self.cap.read()
        if success:
            frame = webcam_frame[...,::-1]
            frame = cv2.resize(frame, (shape[1], shape[0]))
        return np.array(frame)


filters.register_filter("webcam", Webcam)
