"""async_client_unix: demo of an asynchronous client w/ user input

Description: 
demonstration of an asynchronous client using calls to select
handles receiving data from server and from the standard input
sends/receives messages to server framed as NULL-terminated messages

NOTE: will only work on UNIX systems, will not work on Windows since
    only sockets can be used with select on Windows

CSI 235
Prof. Joshua Auerbach
April 24, 2017
"""


import select
import socket
from sys import stdin

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

def handle_session(server_sock):
    """Purpose: handle a session between client and server

    Pre: server_sock is a socket connected to the server
    Post: will return once connection is closed
    """
    # create data structures for the sockets
    bytes_received = {}

    bytes_to_send = b'' # only ever sending on server_sock so just one buffer
    
    input_sockets = [stdin, server_sock]
    output_sockets = []

    while True:
        readable, writeable, _ = select.select(input_sockets,output_sockets, [])
        
        for sock in readable:   
            
            if sock == stdin:
                # if it is the stdin, then user input avail, get message,
                # frame it and put in buffer to send
                message = stdin.readline().strip() # strip off trailing \n
                bytes_to_send += message.encode() + b'\x00'

                # if we were not previously interested in being able to write
                # on the server socket, we are now (since have data to send)
                if not server_sock in output_sockets:
                    output_sockets.append(server_sock)
            
            else:
                # otherwise we have data to read from the server
                more_data = sock.recv(4096)

                if not more_data:
                    server_sock.close()
                    print "Disconnected"
                    return

                # concatenate with existing data
                data = bytes_received.pop(sock, b'') + more_data

                if data.endswith(b'\x00'):
                    # have a whole message, print to screen
                    print 'Received: ', data[:-1].decode()
                else :
                    # have partial message, buffer what we have
                    bytes_received[sock] = data

        for sock in writeable:
            if sock != server_sock:
                # sanity check: should never be here except with server_sock
                raise Exception("Unexpected output event!")
            
            # try to send message
            n = server_sock.send(bytes_to_send)
            if n < len(bytes_to_send):
                # if did not send all, re-buffer the rest
                bytes_to_send = bytes_to_send[n:]
            else:
                # if sent all, reset buffer and stop listening for output events
                bytes_to_send = b''
                output_sockets.remove(server_sock)


        

if __name__ == '__main__':
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect( (SERVER_IP, SERVER_PORT) )
    server_sock.setblocking(False)
    
    handle_session(server_sock)
