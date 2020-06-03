import filters
import cv2
import numpy as np


class Noise:
    @classmethod
    def config(cls):
        return {}

    def __init__(self, *args, **kwargs):
        pass

    def apply(self, *args, **kwargs):
        frame = kwargs['frame']
        noise = np.zeros((frame.shape[0], frame.shape[1], 4))
        indices = (np.random.random(frame.shape[:2]) < 0.05)
        frame[indices,:] = 255
        return frame

filters.register_filter("noise", Noise)
