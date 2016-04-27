#!/bin/python
# -*- coding:utf-8 -*-

'''
    simple chat

    TCP socket client
'''


import socket
import sys
import time
import thread


class Server(object):
    def __init__(self, host, port, connectionsMax):
        self.host = host
        self.port = port
        self.connectionsMax = connectionsMax
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'Socket created'
        try:
            self.server.bind((self.host, self.port))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            self.socket.close()
            sys.exit(0)
        print 'Socket bind complete'
        self.server.listen(self.connectionsMax)
        self.connectedList = []
        self.addrList = []
        self.userList = []
        self.connections = 0

        self.msgExit = 'exit'

    def searchConnection(self):
        connData = self.server.accept()
        assert isinstance(connData, object)
        return connData

    def sendData(self, conn, data):
        # type: (object, object) -> object
        conn.send(data)

    def receiveData(self, conn):
        data = conn.recv(1024)
        return data

    def endConnection(self):
        self.server.close()


def validatesConnection(server):  # validates saved connections
    pass


def sendData(server, conn):
    control = True
    while control:
        data = server.receiveData(conn)

        if not data: break

        print 'receive: ', data

        if data == server.msgExit:
            control = False
            data = 'user saiu da sala'

        for connTemp in server.connectedList:
            if connTemp != conn:
                server.sendData(connTemp,data)

    for i, connTemp in enumerate(server.connectedList):
        if connTemp == conn: break

    del server.addrList[i]
    # del server.userList[i]
    del server.connectedList[i]
    server.connections -= 1

    conn.close()
    print 'conection close ', conn


def searchConnection(server):  # search the connections being made
    """

    :type server: object
    """
    try:
        while True:
            conn, addr = server.searchConnection()
            if not server.connectionsMax < server.connections:
                thread.start_new_thread(sendData,(server,conn))
                print '\nConnected'
                print 'conn: ', conn
                print 'addr: ', addr
                server.connections += 1
                server.connectedList.append(conn)
                server.addrList.append(addr)
            else:
                assert isinstance(conn.send, object)
                conn.send("ERROcrowdedServer")
                conn.close()
                print 'crowdedServer\n'
    except KeyboardInterrupt:  # CTRL+C
        print 'Going out'
        server.endConnection()
        sys.exit(0)


if __name__ == '__main__':
    host = ''
    port = 12000
    connectionsMax = 15

    print 'host: ', host
    print 'port: ', port

    server = Server(host, port, connectionsMax)

    time.sleep(0.4)
    print '\nServer ready...'

    searchConnection(server)

    while True:
        pass
