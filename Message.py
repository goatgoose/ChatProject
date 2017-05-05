"""
    Author: Sam Clark
    Class: CSI-235-02
    Assignment: Final Project
    Date Assigned: 4/17/2017
    Due Date: 5/5/2017, 11:59 PM
    Description:
    Asynchronous chat client and server
    Certification of Authenticity:
    I certify that this is entirely my own work, except where I have given
    fully-documented references to the work of others. I understand the
    definition and consequences of plagiarism and acknowledge that the assessor
    of this assignment may, for the purpose of assessing this assignment:
    - Reproduce this assignment and provide a copy to another member of
    academic staff; and/or
    - Communicate a copy of this assignment to a plagiarism checking
    service (which may then retain a copy of this assignment on its database
    for the purpose of future plagiarism checking)
 """


import time


class Message:
    """A simple class to handle messages"""
    def __init__(self, msg_tuple):
        """
        pre: msg_tuple is a valid message
        post: initializes Message's member variables, throws InvalidMessageError if its an invalid message
        purpose: creates a new Message
        """
        if len(msg_tuple) != 4:
            raise InvalidMessageError()

        self.source = msg_tuple[0]
        self.dest = msg_tuple[1]
        self.timestamp = msg_tuple[2]
        self.content = msg_tuple[3]

    def as_tuple(self):
        """
        pre: none
        post: none
        purpose: gets the tuple representation of the message
        """
        msg_tuple = (self.source, self.dest, self.timestamp, self.content)
        return msg_tuple

    def pretty_print(self):
        """
        pre: none
        post: none
        purpose: gets a string representation of the message
        """
        pretty_string = ""
        # http://stackoverflow.com/questions/12400256/python-converting-epoch-time-into-the-datetime
        pretty_string += time.strftime("%H:%M:%S", time.localtime(self.timestamp)) + " - "
        if self.dest != "ALL":
            pretty_string += "DM -  "
        pretty_string += self.source + ":  "
        pretty_string += self.content
        return pretty_string


class InvalidMessageError(ValueError):
    """
    Raise when the incoming json string is invalid
    """
