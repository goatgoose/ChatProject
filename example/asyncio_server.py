#!/usr/bin/env python3
"""asyncio_server: demo of an asynchronous server using asyncio callbacks

Description: 
demonstration of an asynchronous server using asyncio callbacks (requires 
Python 3.4 or newer)
for each conneciton will receive NULL-terminated messages and send to 
all clients

CSI 235
Prof. Joshua Auerbach
April 17, 2017
"""
import asyncio

SERVER_INTERFACE = ''
SERVER_PORT = 8080
BUFFER_SIZE = 4096

class SimpleServer(asyncio.Protocol):

    # class level variable for keeping track of open transport objects
    transports = []

    def connection_made(self, transport):
        self.transport = transport
        self.address = transport.get_extra_info("peername")
        self.data = b''
        print('Accepted connection from {}'.format(self.address))
        SimpleServer.transports.append(transport)
        
    def data_received(self, data):
        self.data += data
        if self.data.endswith(b'\x00'):
            # note that we use transport.write rather than directly
            # sending on the socket
            # send message to all clients (including one that sent message)
            for transport in SimpleServer.transports:
                transport.write(self.data)
            self.data = b''
            
    def connection_lost(self, exc):
        if exc:
            print('Client {} error: {}'.format(self.address, exc))
        elif self.data:
            print('Client {} sent {} but then closed'.format(self.address, self.data))
        else:
            print('Client {} closed normally'.format(self.address))
        SimpleServer.transports.remove(self.transport)
            
if __name__ == '__main__':
    address = (SERVER_INTERFACE, SERVER_PORT)
    loop = asyncio.get_event_loop()
    
    server = loop.run_until_complete(loop.create_server(SimpleServer, *address))
    
    print ('Listening at {}'.format(SERVER_PORT))
    try:
        loop.run_forever()
    finally:
        server.close()
        loop.close()
