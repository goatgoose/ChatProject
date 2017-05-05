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
 """


import socket


class EightBallClient:
    """
    A client that asks questions to EightBallServer
    """
    def __init__(self):
        """
        pre: none
        post: none
        purpose: sets the member variables for a new Client
        """
        self.HOST = "127.0.0.1"
        self.PORT = 8001
        self.BUFFER_SIZE = 4096

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))

    def start(self):
        """
        pre: none
        post: asks for questions until exited
        purpose: starts the client
        """
        while True:
            question = raw_input("Enter question or type exit: ")
            if question.lower() == "exit":
                self.close_connection()
                break

            if not question.endswith("?"):
                question += "?"

            self.send_question(question)
            print(self.receive_response())
            print("")

    def send_question(self, question):
        """
        pre: none
        post: none
        purpose: sends a question to the server
        """
        self.sock.send(question)

    def receive_response(self):
        """
        pre: none
        post: none
        purpose: gets the response from the server
        """
        data = ""
        while True:
            more_data = self.sock.recv(self.BUFFER_SIZE)
            delimiter_index = -1
            if "." in more_data:
                delimiter_index = more_data.find(".")
            elif "!" in more_data:
                delimiter_index = more_data.find("!")

            if delimiter_index != -1:
                data = data + more_data[:delimiter_index + 1]
                return data
            else:
                data = data + more_data

    def close_connection(self):
        """
        pre: none
        post: none
        purpose: closes the connection with the server
        """
        self.sock.close()
        print("connection closed")


if __name__ == "__main__":
    client = EightBallClient()
    client.start()
