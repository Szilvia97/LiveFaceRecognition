from dataclasses import dataclass

@dataclass
class FaceDetectionData:
    """A class for holding a detection content"""
    score: float
    text: str
    startX: int
    startY: int
    endX: int
    endY: int
