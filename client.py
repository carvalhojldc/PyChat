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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
        except socket.error as msg:
            print 'Connect failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            self.socket.close()
            sys.exit(0)

        self.requestPrivateCommunication = False
        self.dataReceive = 0
        self.controlLoop = True

    def sendData(self, data):
        self.socket.send(data)

    def receiveData(self):
        data = self.socket.recv(10024)
        return data

    def endConnection(self):
        self.socket.close()


def receiveData(client):
    try:
        while client.controlLoop is True:
            client.dataReceive = client.receiveData()

            if client.dataReceive[0] == '+':
                trash, client.dataReceive = client.dataReceive.split('+')
                client.dataReceive = str(client.dataReceive) + ' gostaria de iniciar uma conversa privada com você.\nyes ou no?'
                client.requestPrivateCommunication = True

            print str(client.dataReceive)
            while client.requestPrivateCommunication: pass

    except KeyboardInterrupt:  # CTRL+C
        print 'Going out'
        client.endConnection()
        sys.exit(1)


def sendData(client):
    try:

        statusServer = client.receiveData()  # server response
        if statusServer == 'ERROcrowdedServer':
            print 'Bate papo lotado\nTente novamente mais tarde'
            sys.exit(1)
        if statusServer == 'connectedServer':
            print 'Instrucoes:\nDigit exit para sair\nDigite pv para solicitar uma conversa privada\n'

            username = None
            while True:
                username = raw_input('Digite um nome de usuário: ')

                if not username: continue

                username = '@' + str(username)
                client.sendData(username) # send username

                reply = client.receiveData() # server response
                print reply

                if reply[0] != '@': # if the username is valid
                    break

            thread.start_new_thread(receiveData, (client,))

            while client.controlLoop is True:

                data = raw_input()

                if not data: continue
                dataTest = data.replace(' ', '')

                if client.requestPrivateCommunication is True:
                    while client.requestPrivateCommunication is True:
                        if data != 'yes' and data != 'no':
                            data = raw_input()
                        else:
                            client.requestPrivateCommunication = False
                            userReceive, temp = client.dataReceive.split(' ',1)
                            data = '!' + str(userReceive) + '!' + str(username)

                elif dataTest == 'pv': # private comunication
                    user = raw_input('Digite o nome do usuario: ')
                    print 'Solicitação em adamento...'
                    data = '#' + username + '#' + user

                elif dataTest == 'exit':
                    client.controlLoop = False
                    data = username + '>>' + data

                else:
                    data = username + '>>' + data + '\n'

                client.sendData(data)

    except KeyboardInterrupt:  # CTRL+C
        print 'Going out...'
        client.endConnection()
        sys.exit(1)


if __name__ == '__main__':
    host = 'localhost'
    port = 12002
    client = Client(host, port)

    sendData(client)

    client.endConnection()
    print 'Conversa finalizada'
    sys.exit(1)