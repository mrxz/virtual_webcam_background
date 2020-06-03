import filters
import cv2
import numpy as np
from scipy import ndimage


class Flip:
    @classmethod
    def config(cls):
        return {
            "Horizontal": {"type": "boolean", "default": True},
            "Vertical": {"type": "boolean", "default": False},
        }

    def __init__(self, horizontal=True, vertical=False, *args, **kwargs):
        self.horizontal = horizontal
        self.vertical = vertical

    def apply(self, *args, **kwargs):
        frame = kwargs['frame']
        if self.horizontal:
            frame = cv2.flip(frame, 1)
        if self.vertical:
            frame = cv2.flip(frame, 0)
        return frame

class Zoom:
    @classmethod
    def config(cls):
        return {
            "Horizontal": {"type": "double", "range": [0.1, 10], "step_size": 0.1, "input": True, "default": 1.0},
            "Vertical": {"type": "double", "range": [0.1, 10], "step_size": 0.1, "input": True, "default": 1.0},
            "Pad and Crop": {"type": "constant", "value": True}
        }

    def __init__(self, horizontal, vertical=None, pad_and_crop=True,
                 *args, **kwargs):
        self.horizontal = horizontal
        if vertical is None:
            vertical = horizontal
        self.vertical = vertical
        self.pad_and_crop = pad_and_crop

    def apply(self, *args, **kwargs):
        frame = kwargs['frame']

        zoomed = ndimage.zoom(frame, (self.vertical, self.horizontal, 1.0),
                              order=0)

        if zoomed.shape[2] == 3:
            # Add alpha channel
            zoomed = np.append(zoomed,
                    np.ones((zoomed.shape[0], zoomed.shape[1], 1)) * 255.0,
                    axis=2)


        if self.pad_and_crop:
            frame = np.zeros((frame.shape[0], frame.shape[1], 4))
            frame[:min(frame.shape[0], zoomed.shape[0]),
                  :min(frame.shape[1], zoomed.shape[1]),
                  :zoomed.shape[2]] = \
            zoomed[:min(frame.shape[0], zoomed.shape[0]),
                  :min(frame.shape[1], zoomed.shape[1]),
                  :zoomed.shape[2]]
        else:
            frame = zoomed

        return frame


class Move:
    @classmethod
    def config(cls):
        return {
            "Horizontal": {"type": "double", "range": [-1024, 1024], "step_size": 0.1, "input": True, "default": 0.0},
            "Vertical": {"type": "double", "range": [-1024, 1024], "step_size": 0.1, "input": True, "default": 0.0},
            "Relative": {"type": "boolean", "default": True},
            "Periodic": {"type": "boolean", "default": False},
        }

    def __init__(self, horizontal, vertical, relative=False, periodic=True,
                 *args, **kwargs):

        self.horizontal = horizontal
        self.vertical = vertical
        self.relative = relative
        self.periodic = periodic

    def apply(self, *args, **kwargs):
        frame = kwargs['frame']

        horizontal = self.horizontal
        vertical = self.vertical
        if self.relative:
            horizontal = int(frame.shape[1] * horizontal)
            vertical =   int(frame.shape[0] * vertical)

        if self.periodic:
            return np.roll(frame,
                           shift=(horizontal, vertical),
                           axis=(1, 0))
        else:
            return ndimage.affine_transform(frame,
                           matrix=[1, 1, 1],
                           offset=[-vertical, -horizontal, 0],
                           order=0)


class Affine:
    @classmethod
    def config(cls):
        return {
            "Matrix": {"type": "constant", "value": [[1,0],[0,1]]},
            "Offset": {"type": "constant", "value": [0,0]}
        }

    def __init__(self, matrix=[[1,0],[0,1]], offset=[0,0], relative=False,
                 *args, **kwargs):

        self.matrix = matrix
        self.offset = offset
        self.relative = relative

        assert(len(matrix) == 2)
        assert(len(matrix[0]) == 2)
        assert(len(matrix[1]) == 2)
        assert(len(offset) == 2)

    def apply(self, *args, **kwargs):
        frame = kwargs['frame']

        matrix = np.zeros((3, 3))
        matrix[0,:2] = self.matrix[0]
        matrix[1,:2] = self.matrix[1]
        matrix[2,2] = 1.0
        offset = self.offset + [0]

        if frame.shape[2] == 3:
            # Add alpha channel
            frame = np.append(frame,
                    np.ones((frame.shape[0], frame.shape[1], 1)) * 255.0,
                    axis=2)

        frame = ndimage.affine_transform(frame,
                       matrix=matrix,
                       offset=offset,
                       order=0)
        return frame


filters.register_filter("flip", Flip)
filters.register_filter("zoom", Zoom)
filters.register_filter("move", Move)
filters.register_filter("affine", Affine)
