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
        self.connectedList = []
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
    for i, userTemp in enumerate(server.userList):
        if userTemp == user:
            conn = server.userList[i + 1]
            break
    return conn


def searchUser(server, user):
    search = False
    for userTemp in server.userList:
        if userTemp == user:
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


def privateConnClear(server, user):
    for i, userTemp in enumerate(server.userList):
        if userTemp == user:
            del server.userList[i]
            del server.userList[i]
            break


def sendData(server, conn):
    user = defineUser(server, conn)

    print str(user) + ' se conectou ao servidor'

    server.userList.append(user)
    server.userList.append(conn)

    # server.userList
    # i%2 == 0 -> user
    # i%2 != 0 -> conn

    msgUER = '\n** ' + str(user) + ' entrou na sala'
    for i,connTemp in enumerate(server.userList): # msg user entered the room
        if connTemp != conn and (i%2 != 0): server.sendData(connTemp, msgUER)

    msg = 'Users connected: '
    for i, user in enumerate(server.userList):
        if i%2 == 0: msg = str(msg) + str(user) + ' '
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
                    server.userList.append(username)
                    server.userList.append(conn)
                    server.userList.append(userDest)
                    server.userList.append(connDest)

                    textExit = '\nA conversa privada foi finalizada\nVocê voltou para o chat público\n'
                    server.sendData(conn, textExit)

                    data = '\n' + str(username) + ' saiu da conversa privada' + str(textExit)
                    server.sendData(connDest, data)

                    for i, dataTemp in enumerate(server.userListPrivate): # clear list
                        if dataTemp[0] == username or dataTemp[0] == userDest:
                            del server.userListPrivate[i]
                            if i % 2 == 0:
                                del server.userListPrivate[i]
                            else:
                                del server.userListPrivate[i-1]

            # end private communication

            else : # public communication
                if endConversation is True:
                    control = False
                    data = username + ' saiu da conversa'

                for i, connTemp in enumerate(server.userList):
                    if i%2 != 0 and connTemp != conn:
                        server.sendData(connTemp, data)

        elif data[0] == '#':  # private communication request
            trash, userSender, userReceiver = data.split('#') # user1 wants to talk to user2
            flagUser = searchUser(server, userReceiver)

            if flagUser is True:
                newData = '+' + userSender
                for i, userTemp in enumerate(server.userList):
                    if userTemp == userReceiver:
                        connReceiver = server.userList[i + 1]
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

            server.userListPrivate.append([])

            position = len(server.userListPrivate) - 1

            server.userListPrivate[position].append(user1)
            server.userListPrivate[position].append(connRes)

            server.userListPrivate.append([])
            position = len(server.userListPrivate) - 1

            server.userListPrivate[position].append(user2)
            server.userListPrivate[position].append(conn)

            privateConnClear(server, user1)
            privateConnClear(server, user2)

    # end while

    for i, connTemp in enumerate(server.connectedList): # clear connectedList
        if connTemp == conn:
            del server.connectedList[i]
            break

    server.connections -= 1

    connTemp = None
    for i, connTemp in enumerate(server.userList): # clear userList
        if connTemp == conn:
            del server.userList[i] # conn
            del server.userList[i-1]  # username
            break

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
                server.connectedList.append(conn)
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
