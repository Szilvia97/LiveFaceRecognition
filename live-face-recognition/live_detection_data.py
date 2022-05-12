from dataclasses import dataclass
import math

@dataclass
class LiveDetectionData:
    """A class for holding a detection content"""
    score: float
    text: str
    startX: int
    startY: int
    endX: int
    endY: int

    def get_COG(self):
        return abs(self.startX - self.endX), abs(self.startY - self.endY)

# TODO: Add method for calculation COG:
# TODO: Add method for text generation: score > config.score? "real": "fake"

