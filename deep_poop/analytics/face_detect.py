import numpy
from typing import List
import face_recognition as fr


class Face(object):
    def __init__(self, landmarks: dict):
        self.chin = landmarks["chin"]
        self.left_eyebrow = landmarks["left_eyebrow"]
        self.right_eyebrow = landmarks["right_eyebrow"]
        self.nose_bridge = landmarks["nose_bridge"]
        self.nose_tip = landmarks["nose_tip"]
        self.left_eye = landmarks["left_eye"]
        self.right_eye = landmarks["right_eye"]
        self.top_lip = landmarks["top_lip"]
        self.bottom_lip = landmarks["bottom_lip"]

    def center_of(self, feature: list) -> tuple:
        """Returns the center of a facial feature.

        Args:
            feature (list): Outline of feature

        Returns:
            tuple: Center of feature (x,y)
        """
        average_x, average_y = 0, 0
        for e in feature:
            average_x += e[0] // len(feature)
            average_y += e[1] // len(feature)
        return (average_x, average_y)


def face_locations(image: numpy.ndarray):
    """Finds all face locations in an image

    Returns:
        tuple: Face box (top, right, bottom, left)
    """

    return fr.face_locations(image)


def image_has_face(image: numpy.ndarray):
    return face_locations(image) != []


def batch_face_locations(images: List[numpy.ndarray], batch_size=128):
    """Finds all face locations in a list of images through batch processing

    Args:
        images (List[numpy.ndarray]): List of images

    Returns:
        List[tuple]: Face boxes (top, right, bottom, left)
    """
    if batch_size < 1:
        raise ValueError
    batch_size = min(batch_size, len(images))
    face_locations = fr.batch_face_locations(
        images, number_of_times_to_upsample=1, batch_size=batch_size
    )
    assert len(face_locations) == len(images)
    return face_locations


def load_image(path: str) -> numpy.ndarray:
    return fr.load_image_file(path)


def face_to_center(face: tuple) -> tuple:
    """Converts a face box tuple into a center tuple

    Args:
        face (tuple): Face box (top, right, bottom, left)

    Returns:
        tuple: Face center (x, y)
    """

    return ((face[1] + face[3]) / 2, (face[0] + face[2]) / 2)


def face_centers(image: numpy.ndarray):
    faces = face_locations(image)
    return [face_to_center(face) for face in faces]


def find_faces(image: numpy.ndarray) -> list:
    """Finds information about all faces in an image.

    Args:
        image (numpy.ndarray): Image

    Returns:
        list: Face objects with facial feature information
    """
    landmarks = fr.face_landmarks(image)
    return [Face(l) for l in landmarks]
