
import select
import socket
from sys import stdin
import struct
import json
import time
import Message


class ChatClient:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 8001
        self.BUFFER_SIZE = 4096

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect((self.HOST, self.PORT))
        self.server_sock.setblocking(False)

        self.bytes_received = {}
        self.bytes_to_send = b''

        self.input_sockets = [stdin, self.server_sock]
        self.output_sockets = []

        self.username = ""
        self.username_verified = False

        self.user_list = []

    def start(self):
        print "Enter a username: "

        while True:
            readable, writeable = select.select(self.input_sockets, self.output_sockets, [])[:2]
            for sock in readable:
                if sock == stdin:
                    message = stdin.readline().strip()
                    if not self.username_verified:
                        self.username = message
                        self.queue_message(json.dumps({
                            "USERNAME": self.username
                        }))
                    else:
                        if len(message) == 0:
                            print "Server has disconnected."
                            sock.close()
                            continue

                        if message[0] == "/":
                            command = message.split(" ")[0][1:]
                            if command.lower() == "help":
                                print "Available commands:"
                                print "/help - displays available commands"
                                print "/list - lists all users connected to server"
                                print "/w [username] [message] - whispers a message to a user"

                            elif command.lower() == "list":
                                for user in self.user_list:
                                    print user

                            elif command.lower() == "w":
                                if len(message.split(" ")) < 3:
                                    print "Invalid usage - /w [username] [message]"
                                    continue

                                message_split = message.split(" ")
                                self.queue_message(json.dumps({
                                    "MESSAGES": [(
                                        self.username,
                                        message_split[1],
                                        int(time.time()),
                                        "".join(message_split[2:])
                                    )]
                                }))
                        else:
                            self.queue_message(json.dumps({
                                "MESSAGES": [(
                                    self.username,
                                    "ALL",
                                    int(time.time()),
                                    message
                                )]
                            }))

                elif sock == self.server_sock:
                    incoming_data = sock.recv(self.BUFFER_SIZE)
                    data = self.bytes_received.pop(sock, b'') + incoming_data
                    msg_length = struct.unpack("!I", data[:4])[0]
                    if len(data) - 4 >= msg_length:
                        self.handle_data(data[4:msg_length + 4])
                        self.bytes_received[sock] = data[msg_length + 4:]
                    else:
                        self.bytes_received[sock] = data

            for sock in writeable:
                bytes_sent = sock.send(self.bytes_to_send)
                if bytes_sent < len(self.bytes_to_send):
                    self.bytes_to_send = self.bytes_to_send[bytes_sent:]
                else:
                    self.bytes_to_send = b''
                    self.output_sockets.remove(self.server_sock)

    def queue_message(self, data):
        self.bytes_to_send += struct.pack("!I", len(data)) + data.encode()
        if self.server_sock not in self.output_sockets:
            self.output_sockets.append(self.server_sock)

    def handle_data(self, data):
        data = json.loads(data)

        if "INFO" in data:
            print data["INFO"]

        if "ERROR" in data:
            print data["ERROR"]

        if "USERNAME_ACCEPTED" in data:
            self.username_verified = data["USERNAME_ACCEPTED"]
            if self.username_verified:
                self.user_list.append(self.username)
                print "Type /help for command information"
            else:
                print "Enter a username: "

        if "USER_LIST" in data:
            self.user_list = data["USER_LIST"]

        if "MESSAGES" in data:
            for msg_tuple in data["MESSAGES"]:
                message = Message.Message(msg_tuple)
                print message.pretty_print()

        if "USERS_JOINED" in data:
            for user in data["USERS_JOINED"]:
                self.user_list.append(user)

        if "USERS_LEFT" in data:
            for user in data["USERS_LEFT"]:
                if user in self.user_list:
                    self.user_list.remove(user)

if __name__ == "__main__":
    client = ChatClient()
    client.start()
