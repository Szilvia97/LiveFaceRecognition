from dataclasses import dataclass


@dataclass
class FaceDetectionData:
    """A class for holding a detection content"""
    name: str
    left: int
    top: int
    right: int
    bottom: int

    def get_COG(self):
        return ((self.left + self.right)/2, (self.top + self.bottom)/2)
