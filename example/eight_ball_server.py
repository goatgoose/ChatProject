"""
    Author: Sam Clark
    Class: CSI-235-02
    Assignment: Lab 7
    Date Assigned: 4/10/2017
    Due Date: 4/17/2017, 11:00 AM
    Description:
    client and server application for a Magic 8-Ball
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

    referred to:
      - https://pymotw.com/2/select/
      - https://docs.python.org/2/library/socket.html
      - provided async_server.py
 """

import select
import socket
import random


class EightBallServer:
    """
    A server responds to questions with a preset list of answers
    """
    def __init__(self):
        """
        pre: none
        post: none
        purpose: sets the member variables for a new Server
        """
        self.INTERFACE = "0.0.0.0"
        self.PORT = 8001
        self.BUFFER_SIZE = 4096

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.INTERFACE, self.PORT))

        # https://en.wikipedia.org/wiki/Magic_8-Ball#Possible_answers
        self.possible_responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely!",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes!",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]

    def start(self):
        """
        pre: none
        post: waits for connections forever
        purpose: starts the server
        """
        self.listener.listen(1)
        print "Listening on port", self.PORT

        sockets = {self.listener.fileno(): self.listener}
        messages_received = {}
        messages_to_send = {}

        poller = select.poll()
        poller.register(self.listener, select.POLLIN)

        while True:
            for fd, event in poller.poll():
                sock = sockets[fd]
                if sock is self.listener:
                    sock, address = self.listener.accept()
                    sock.setblocking(False)
                    sockets[sock.fileno()] = sock
                    poller.register(sock, select.POLLIN)

                # data in
                elif event & select.POLLIN:
                    incoming_data = sock.recv(self.BUFFER_SIZE)

                    data = messages_received.pop(sock, "") + incoming_data
                    if data.endswith("?"):
                        print("question received: " + data)
                        # http://stackoverflow.com/questions/3996904/generate-random-integers-between-0-and-9
                        messages_to_send[sock] = self.possible_responses[random.randint(0,
                                                                         len(self.possible_responses) - 1)]
                        poller.modify(sock, select.POLLOUT)
                    else:
                        messages_received[sock] = data

                # data out
                elif event & select.POLLOUT:
                    data = messages_to_send.pop(sock)
                    bytes_sent = sock.send(data)

                    if bytes_sent < len(data):
                        messages_to_send[sock] = data[bytes_sent:]
                    else:
                        poller.modify(sock, select.POLLIN)

                # close / error
                elif event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                    print("connection closed")
                    poller.unregister(fd)
                    sock.close()
                    del sockets[fd]


if __name__ == "__main__":
    server = EightBallServer()
    server.start()
