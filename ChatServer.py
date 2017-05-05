
import socket
import select
import queue
import struct
import json
import Message


class ChatServer:
    def __init__(self):
        self.INTERFACE = "0.0.0.0"
        self.PORT = 8001
        self.BUFFER_SIZE = 4096

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.INTERFACE, self.PORT))

        self.sockets = {}  # fileno : socket
        self.user_sockets = {}  # username : socket
        self.data_received = {}  # socket : data
        self.data_to_send = {}  # socket : data

        self.chat_log = []

    def start(self):
        self.listener.listen(1)
        print "Listening on port", self.PORT

        self.sockets[self.listener.fileno()] = self.listener

        self.poller = select.poll()
        self.poller.register(self.listener, select.POLLIN)

        while True:
            for fd, event in self.poller.poll():
                sock = self.sockets[fd]
                if sock is self.listener:
                    sock, address = self.listener.accept()
                    sock.setblocking(False)
                    self.sockets[sock.fileno()] = sock
                    self.poller.register(sock, select.POLLIN)

                # data in
                elif event & select.POLLIN:
                    incoming_data = sock.recv(self.BUFFER_SIZE)
                    data = self.data_received.pop(sock, b'') + incoming_data
                    msg_length = struct.unpack("!I", data[:4])[0]

                    if len(data) - 4 >= msg_length:
                        self.data_received[sock] = data[msg_length + 4:]
                        self.handle_data(sock, data[4:msg_length + 4])
                    else:
                        self.data_received[sock] = data

                # data out
                elif event & select.POLLOUT:
                    data = self.data_to_send[sock]
                    bytes_sent = sock.send(data)
                    if bytes_sent < len(data):
                        self.data_to_send[sock] = data[bytes_sent:]
                    else:
                        self.data_to_send[sock] = b''
                        self.poller.modify(sock, select.POLLIN)

                # close / error
                elif event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                    print "connection closed"
                    self.poller.unregister(fd)
                    sock.close()
                    del self.sockets[fd]
                    # TODO tell client user disconnected

    def queue_message(self, sock, data):
        to_send = self.data_to_send.pop(sock, b'')
        to_send += struct.pack("!I", len(data)) + data.encode()
        self.data_to_send[sock] = to_send
        self.poller.modify(sock, select.POLLOUT)

    def handle_data(self, sock, data):
        data = json.loads(data)
        if "USERNAME" in data:
            username = data["USERNAME"]
            if sock in self.user_sockets.values():
                self.queue_message(sock, json.dumps({
                    "USERNAME_ACCEPTED": False,
                    "INFO": "Client already has a username."
                }))
            elif username in self.user_sockets:
                self.queue_message(sock, json.dumps({
                    "USERNAME_ACCEPTED": False,
                    "INFO": "Username already exists."
                }))
            elif " " in username:
                self.queue_message(sock, json.dumps({
                    "USERNAME_ACCEPTED": False,
                    "INFO": "Spaces not allowed in usernames."
                }))
            else:
                self.queue_message(sock, json.dumps({
                    "USERNAME_ACCEPTED": True,
                    "INFO": "Welcome!",
                    "USER_LIST": self.user_sockets.values(),
                    "MESSAGES": self.chat_log
                }))
                for user_sock in self.user_sockets:
                    self.queue_message(user_sock, json.dumps({
                        "USERS_JOINED": username
                    }))
                self.user_sockets[sock] = username

        if "MESSAGES" in data:
            for msg_tuple in data["MESSAGES"]:
                self.chat_log.append(msg_tuple)
                message = Message.Message(msg_tuple)
                if message.dest != "ALL":  # its a dm
                    if message.dest not in self.user_sockets:
                        self.queue_message(sock, json.dumps({
                            "ERROR": "User: " + message.dest + " does not exist."
                        }))
                    else:
                        self.queue_message(self.user_sockets[message.dest], json.dumps({
                            "MESSAGES": [msg_tuple]
                        }))
                else:
                    for user_sock in self.user_sockets:
                        if user_sock == sock:
                            continue
                        self.queue_message(user_sock, json.dumps({
                            "MESSAGES": [msg_tuple]
                        }))

if __name__ == "__main__":
    server = ChatServer()
    server.start()
