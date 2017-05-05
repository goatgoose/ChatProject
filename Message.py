
import json


class Message:
    def __init__(self, msg_tuple):
        if len(msg_tuple) != 4:
            raise InvalidMessageError()

        self.source = msg_tuple[0]
        self.dest = msg_tuple[1]
        self.timestamp = msg_tuple[2]
        self.content = msg_tuple[3]

    def as_tuple(self):
        msg_tuple = (self.source, self.dest, self.timestamp, self.content)
        return msg_tuple


class InvalidMessageError(ValueError):
    """
    Raise when the incoming json string is invalid
    """
