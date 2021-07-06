#! /usr/bin/env python

import socket
import sys
import time
import threading
import select
import traceback

# a biblioteca abaixo será para serializar e de-serializar a chave e o 
# vetor de inicialização que será passado aos clientes
import pickle


class Server(threading.Thread):
    def initialise(self, receive):
        self.receive = receive

    def run(self):
        lis = []
        lis.append(self.receive)
        while 1:
            read, write, err = select.select(lis, [], [])
            for item in read:
                try:
                    s = item.recv(1024)
                    if s != '':
                        chunk = s
                        print(chunk.decode() + '\n>>')
                except:
                    traceback.print_exc(file=sys.stdout)
                    break


class Client(threading.Thread):
    def connect(self, host, port):
        self.sock.connect((host, port))

    def client(self, host, port, msg):
        sent = self.sock.send(msg)
        # print "Sent\n"

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            host = input("Digite o IP do servidor:\n>>")
            port = int(input("Digite a porta de conexão ao servidor:\n>>"))
        except EOFError:
            print("Erro")
            return 1

        print("Conectando\n")
        s = ''
        self.connect(host, port)

        # após a conexão, o cliente recebe a chave de criptografia do servidor
        # esta será a chave que ficará responsável por encriptar as mensagens 
        # entre clientes 
        output = pickle.loads(self.sock.recv(1024))

        user_name = input("Digite o nome do usuário a ser utilizado:\n>>")
        receive = self.sock
        time.sleep(1)
        srv = Server()
        srv.initialise(receive)
        srv.daemon = True
        print("Iniciando Serviço")
        srv.start()
        while 1:
            # print "Waiting for message\n"
            msg = input('>>')
            if msg == 'saída':
                break
            if msg == '':
                continue
            # print "Sending\n"
            msg = user_name + ': ' + msg
            data = msg.encode()
            self.client(host, port, data)
        return (1)


if __name__ == '__main__':
    print("Iniciando Cliente")
    cli = Client()
    cli.start()