#!/bin/python
# -*- coding:utf-8 -*-

'''
    simple chat

    TCP socket client
'''


import socket
import sys
import thread


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        except socket.error as msg_e:
            print 'Unable to start client.\n', msg_e
            self.socket.close()
            sys.exit(0)

    def sendData(self, data):
        # type: (object) -> object
        self.socket.send(data)

    def receiveData(self):
        data = self.socket.recv(1024)
        return data

    def endConnection(self):
        self.socket.close()

def receiveData(client):
    try:
        while True:
            data = client.receiveData()
            print data
    except KeyboardInterrupt:  # CTRL+C
        print 'Going out'
        client.endConnection()
        sys.exit(1)


def sendData(client):
    try:
        thread.start_new_thread(receiveData, (client,))
        print 'Digit exit para sair'
        username = raw_input('Qual o nome do usuario?')
        data = 0
        controlLoop = True
        while controlLoop:
            data = raw_input()
            if data == 'exit':
                controlLoop = False
            elif data == 'privateMessage':
                user = raw_input('Digite o nome do usuario: ')
                data = '@' + data
            else:
                data = username + '>>' + data
            client.sendData(data)
    except KeyboardInterrupt:  # CTRL+C
        print 'Going out...'
        client.endConnection()
        sys.exit(1)


if __name__ == '__main__':
    host = ''
    port = 12000
    client = Client(host, port)

    sendData(client)

