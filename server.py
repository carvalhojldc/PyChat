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
            self.server.bind(('', self.port))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            self.socket.close()
            sys.exit(0)

        self.server.listen(self.connectionsMax)

        self.userListPrivate = []
        self.userList = []
        self.connections = 0

        self.showPublicCommunication = True

    def searchConnection(self):
        connData = self.server.accept()
        assert isinstance(connData, object)
        return connData

    def sendToAll(self, conn, data):
        for dataTemp in self.userList:  # msg user entered the room
            connTemp = dataTemp[1]
            if connTemp != conn:
                connTemp.send(data)

    def sendToMe(self, conn, data):
        conn.send(data)

    def sendPrivate(self, conn, data):
        conn.send(data)

    def receiveData(self, conn):
        data = conn.recv(10024)
        return data

    def endConnection(self):
        self.server.close()

    def searchUser(self, data):
        for dataTemp in self.userList:
            for dataTemp2 in dataTemp:
                if dataTemp2 == data:
                    return True
        
        for dataTemp in self.userListPrivate:
            for dataTemp2 in dataTemp:
                if dataTemp2 == data:
                    return True
                    
        return False

    def defineUser(self, conn):
        while True:
            username = server.receiveData(conn)
            if not username: continue

            if self.searchUser(username) is True:
                server.sendToMe(conn, str(username) + ' já está sendo utilizado.')
            else:
                self.userList.append([])
                id = len(self.userList) - 1
                self.userList[id].append(username)
                self.userList[id].append(conn)
                return username

    def saveUser(self, username, conn):
        self.userList.append([])
        id = len(self.userList) - 1
        self.userList[id].append(username)
        self.userList[id].append(conn)

    def getUser(self, data):
        user = []
        for i, dataTemp in enumerate(self.userList):
            if dataTemp[0] == data or dataTemp[1] == data:
                user.append(dataTemp[0])
                user.append(dataTemp[1])
                user.append(i)
                return user
        return None

    def setUsersCommunicationPivate(self, username1, conn1, username2, conn2):
        # userListPrivate -> username1, conn1, username2, conn2

        self.userListPrivate.append([])
        id = len(self.userListPrivate) - 1
        # 1º user
        self.userListPrivate[id].append(username1)
        self.userListPrivate[id].append(conn1)
        # 2º user
        self.userListPrivate[id].append(username2)
        self.userListPrivate[id].append(conn2)

    def getUserCommunicationPivate(self, data):
        user = []
        for dataTemp in self.userListPrivate:
            for j, dataTemp_2 in enumerate(dataTemp):
                if dataTemp_2 == data:
                    if j < 2:
                        user.append(dataTemp[2])
                        user.append(dataTemp[3])
                    else:
                        user.append(dataTemp[0])
                        user.append(dataTemp[1])
                    return user
        return None

    def clearList(self, dataList, data):
        for i, dataTemp in enumerate(dataList):
            for dataTemp2 in dataTemp:
                if dataTemp2 == data:
                    if len(dataTemp) == 4:
                        msg = '\nConversa privada encerrada!\n'
                        if data == dataTemp[0] or data == dataTemp[1]:
                            self.saveUser(dataTemp[2], dataTemp[3])
                            self.sendPrivate(dataTemp[3], msg)
                        else:
                            self.saveUser(dataTemp[0], dataTemp[1])
                            self.sendPrivate(dataTemp[1], msg)
                    del dataList[i]
                    return True
        return False

    def clearAll_Lists(self, data):
        self.clearList(self.userList, data)
        self.clearList(self.userListPrivate, data)


def sendData(server, conn):
    user = server.defineUser(conn)

    print str(user) + ' se conectou ao servidor'

    msg = '\n** ' + str(user) + ' entrou na sala'
    server.sendToAll(conn, msg)

    msg = 'Users connected: '
    for dataTemp in server.userList:
        msg = str(msg) + str(dataTemp[0]) + ' '
    server.sendToMe(conn, msg)

    control = True # control while

    while control:
        data = server.receiveData(conn)

        if not data: break

        print data

        if data[0] == '@': # receiving messages
            username, msgReceive = data.split('>>', 1)

            msgReceive = msgReceive.replace(' ', '')
            msgReceive = msgReceive.replace('\n','')

            endConversation = False
            if msgReceive == 'exit' or msgReceive == 'exitp':
                endConversation = True

            uerCoPrivate = []
            uerCoPrivate = server.getUserCommunicationPivate(username)

            if uerCoPrivate is not None: # private communication
                userDest = uerCoPrivate[0]
                connDest = uerCoPrivate[1]

                if endConversation is False:
                    server.sendPrivate(connDest, data)
                else:
                    textExit = '\nA conversa privada foi finalizada\nVocê voltou para o chat público\n'
                    server.sendPrivate(conn, textExit)

                    data = '\n' + str(username) + ' saiu da conversa privada' + str(textExit)
                    server.sendPrivate(connDest, data)

                    # userList -> public
                    server.saveUser(username, conn)
                    server.saveUser(userDest, connDest)

                    server.clearList(server.userListPrivate, username)
            else : # public communication
                if endConversation is True:
                    control = False
                    data = username + ' saiu da conversa'

                server.sendToAll(conn, data)

        elif data[0] == '#':  # private communication request
            trash, userSender, userReceiver = data.split('#') # user1 wants to talk to user2

            if userSender == userReceiver:
                server.sendToMe(conn, '\nUsuário inválido!\n')
            else:
                userReceiverData = []
                userReceiverData = server.getUser(userReceiver)

                if userReceiverData is not None:
                    newData = '+' + userSender
                    connUserReceiver = userReceiverData[1]
                    server.sendPrivate(connUserReceiver, newData)
                else:
                    server.sendToMe(conn, '\nUsuário inválido!\n')


        elif data[0] == '!': # private communication accepted
            trash, user1, user2 = data.split('!')

            msgUser1 = '\n' + str(user2) + ' aceitou a conversa privada\nPara sair digite exitp'
            msgUser2 = '\nVoce esta em um conversa privada com ' + str(user1) + '\nPara sair digite exitp\n'

            userRes = server.getUser(user1)
            connRes = userRes[1]
            server.sendPrivate(connRes, msgUser1)
            server.sendPrivate(conn, msgUser2)

            server.clearList(server.userList, user1)
            server.clearList(server.userList, user2)

            server.setUsersCommunicationPivate(user1, connRes, user2, conn)


    server.clearAll_Lists(conn)
    server.connections -= 1
    conn.close()

    print '\nstatus server: connections = ', server.connections

def searchConnection(server):  # maps new connections
    try:
        while True:
            conn, addr = server.searchConnection() # from class
            if server.connectionsMax > server.connections:
                thread.start_new_thread(sendData, (server, conn)) # a thread for each connection
                print '\nConnected'
                conn.send("connectedServer")
                print 'conn: ', conn
                server.connections += 1
            else: # server full
                assert isinstance(conn.send, object)
                conn.send("ERROcrowdedServer")
                conn.close()

    except KeyboardInterrupt:  # CTRL+C
        print 'Going out'
        server.endConnection()
        sys.exit(0)


if __name__ == '__main__':
    host = 'localhost'
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

