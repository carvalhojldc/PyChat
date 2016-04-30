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

        self.server.listen(self.connectionsMax)

        self.userListPrivate = []
        self.userList = []
        self.connections = 0

    def searchConnection(self):
        connData = self.server.accept()
        assert isinstance(connData, object)
        return connData

    def sendData(self, conn, data):
        conn.send(data)

    def receiveData(self, conn):
        data = conn.recv(10024)
        return data

    def endConnection(self):
        self.server.close()

# end Class Server

def getConn(server, user):
    conn = None
    for dataTemp in server.userList:
        if dataTemp[0] == user:
            conn = dataTemp[1]
            break
    return conn


def searchUser(server, user):
    search = False
    for dataTemp in server.userList:
        if dataTemp[0] == user:
            search = True
            break
    return search


def defineUser(server, conn):
    userInvalid = True
    user = None

    while userInvalid is True:
        userInvalid = False
        user = server.receiveData(conn)

        if not user: continue

        userInvalid = searchUser(server, user)

        if userInvalid is True:
            server.sendData(conn, str(user) + ' já está sendo utilizado.')

    return user


def privateCommunication(server, conn, username, data, idUser_PrivateConversation, endConversation):
    if idUser_PrivateConversation % 2 == 0:
        userDest = server.userListPrivate[idUser_PrivateConversation + 1][0]
    else:
        userDest = server.userListPrivate[idUser_PrivateConversation - 1][0]

    connDest = None
    for dataTemp in server.userListPrivate:
        if dataTemp[0] == userDest:
            connDest = dataTemp[1]

    if endConversation is False:
        server.sendData(connDest, data)
    else:
        addDataUserList(server.userList, conn, username)
        addDataUserList(server.userList, connDest, userDest)

        textExit = '\nA conversa privada foi finalizada\nVocê voltou para o chat público\n'
        server.sendData(conn, textExit)

        data = '\n' + str(username) + ' saiu da conversa privada' + str(textExit)
        server.sendData(connDest, data)

        for i, dataTemp in enumerate(server.userListPrivate):  # clear list
            if dataTemp[0] == username or dataTemp[0] == userDest:
                del server.userListPrivate[i]
                if i % 2 == 0:
                    del server.userListPrivate[i]
                else:
                    del server.userListPrivate[i - 1]

# end private communication


def publicCommunication(server, conn, data):
    for dataTemp in server.userList:
        if dataTemp[1] != conn:
            server.sendData(dataTemp[1], data)
# end public communication


def addDataUserList(listUser, conn, user):
    listUser.append([])
    position = len(listUser) - 1

    listUser[position].append(user)
    listUser[position].append(conn)


def privateConnClear(server, user):
    for i, dataTemp in enumerate(server.userList):
        if dataTemp[0] == user:
            del server.userList[i]
            break


def sendData(server, conn):
    user = defineUser(server, conn)

    print str(user) + ' se conectou ao servidor'

    addDataUserList(server.userList,conn,user)

    msgUER = '\n** ' + str(user) + ' entrou na sala'
    for dataTemp in server.userList: # msg user entered the room
        if dataTemp[1] != conn:
            server.sendData(dataTemp[1], msgUER)

    msg = 'Users connected: '
    for dataTemp in server.userList:
        msg = str(msg) + str(dataTemp[0]) + ' '
    server.sendData(conn, msg)

    control = True # control while

    while control:
        data = server.receiveData(conn)

        if not data: break

        print data

        if data[0] == '@': # receiving messages
            username, msgReceive = data.split('>>', 1)

            privateConversation = False
            idUser_PrivateConversation = 0
            endConversation = False

            msgReceive = msgReceive.replace(' ', '')
            msgReceive = msgReceive.replace('\n','')

            if msgReceive == 'exit' or msgReceive == 'exitp':
                endConversation = True

            # checking if user is in private conversation list
            for i, userTemp in enumerate(server.userListPrivate):
                if userTemp[0] == username: # run names
                    privateConversation = True
                    idUser_PrivateConversation = i
                    break

            if privateConversation is True: # private communication
                privateCommunication(server, conn, username, data, idUser_PrivateConversation, endConversation)
            else : # public communication
                if endConversation is True:
                    control = False
                    data = username + ' saiu da conversa'

                publicCommunication(server, conn, data)

        elif data[0] == '#':  # private communication request
            trash, userSender, userReceiver = data.split('#') # user1 wants to talk to user2
            flagUser = searchUser(server, userReceiver)

            if userSender == userReceiver:
                flagUser = False

            if flagUser is True:
                newData = '+' + userSender
                for dataTemp in server.userList:
                    if dataTemp[0] == userReceiver:
                        connReceiver = dataTemp[1]
                        break
                server.sendData(connReceiver, newData)
            else:
                server.sendData(conn, '\nUsuário inválido!\n')

        elif data[0] == '!': # private communication accepted
            trash, user1, user2 = data.split('!')

            msgUser1 = '\n' + str(user2) + ' aceitou a conversa privada\nPara sair digite exitp'
            msgUser2 = '\nVoce esta em um conversa privada com ' + str(user1) + '\nPara sair digite exitp\n'

            connRes = getConn(server, user1)
            server.sendData(connRes, msgUser1)
            server.sendData(conn, msgUser2)

            addDataUserList(server.userListPrivate, connRes, user1)
            addDataUserList(server.userListPrivate, conn, user2)

            privateConnClear(server, user1)
            privateConnClear(server, user2)

    # end while

    connTemp = None
    for i, dataTemp in enumerate(server.userList): # clear userList
        if dataTemp[1] == conn:
            del server.userList[i] # conn
            break

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
    port = 12002
    connectionsMax = 15

    print 'host: ', host
    print 'port: ', port

    server = Server(host, port, connectionsMax)

    time.sleep(0.4)
    print '\nServer ready...'

    searchConnection(server)

    while True:
        pass
