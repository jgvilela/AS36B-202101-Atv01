#! /usr/bin/env python
import socket
import sys
import traceback
import threading
import select

# as bibliotecas abaixo foram importadas para suportar a criptografia AES
# e a biblioteca "os" é para poder gerar um número aleatório
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib
import os

# já a biblioteca abaixo será para serializar e de-serializar a chave e o 
# vetor de inicialização que será passado aos clientes
import pickle

SOCKET_LIST = []
TO_BE_SENT = []
SENT_BY = {}

# abaixo uma senha é feita, apra que seja criada a chave de criptografia
# que dará conta de criptografar todas as mensagens entre os usuários
chave = os.urandom(32)
vetor_inicializacao = os.urandom(16)

cryptoItems = {}
type(cryptoItems)
cryptoItems['c'] = chave
cryptoItems['v'] = vetor_inicializacao
output = pickle.dumps(cryptoItems)

class Server(threading.Thread):

    def init(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.bind((socket.gethostbyname(socket.gethostname()), 5535))
        self.sock.listen(2)
        SOCKET_LIST.append(self.sock)
        print("Servidor iniciado na porta 5535")

    def run(self):
        while 1:
            read, write, err = select.select(SOCKET_LIST, [], [], 0)
            for sock in read:
                if sock == self.sock:
                    sockfd, addr = self.sock.accept()
                    print(str(addr))
                    sockfd.send(output)

                    SOCKET_LIST.append(sockfd)
                    print(SOCKET_LIST[len(SOCKET_LIST) - 1])

                else:
                    try:
                        s = sock.recv(1024)
                        if s == '':
                            print(str(sock.getpeername()))
                            continue
                        else:
                            TO_BE_SENT.append(s)
                            SENT_BY[s] = (str(sock.getpeername()))
                    except:
                        print(str(sock.getpeername()))


class handle_connections(threading.Thread):
    def run(self):
        while 1:
            read, write, err = select.select([], SOCKET_LIST, [], 0)
            for items in TO_BE_SENT:
                for s in write:
                    try:
                        if (str(s.getpeername()) == SENT_BY[items]):
                            print("Ignorando %s" % (str(s.getpeername())))
                            continue
                        print("Enviando para %s" % (str(s.getpeername())))
                        s.send(items)

                    except:
                        traceback.print_exc(file=sys.stdout)
                TO_BE_SENT.remove(items)
                del (SENT_BY[items])


if __name__ == '__main__':
    srv = Server()
    srv.init()
    srv.start()
    print(SOCKET_LIST)
    handle = handle_connections()
    handle.start()