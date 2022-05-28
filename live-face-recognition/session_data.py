from dataclasses import dataclass


@dataclass
class SessionData:
    """A class for holding a session content"""
    subject: str
    type: str
    className: str
    week: str
    classroom: int
    date: str
    time: str

   