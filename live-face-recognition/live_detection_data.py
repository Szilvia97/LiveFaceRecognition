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
        return ((self.startX + self.endX)/2, (self.startY + self.endY)/2)


