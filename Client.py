#! /usr/bin/env python

import socket
import sys
import time
import threading
import select
import traceback

# as bibliotecas abaixo foram importadas para suportar a criptografia AES
# e a biblioteca "os" é para poder gerar um número aleatório
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# a biblioteca unidecode "normaliza" a mensagem para que a mesma não 
# contenha acentos. Isso porquê quando o caracter ascii tem acentos
# a função de encrypt logo abaixo, diz que a mensagem não está com
# o tamanho múltiplo de 16, necessário para a criptografia. 
import unidecode

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
                        decryptor = cifra.decryptor()
                        message = decryptor.update(s) + decryptor.finalize()
                        print(message.decode().rstrip() + '\n>>')
                except:
                    traceback.print_exc(file=sys.stdout)
                    break


class Client(threading.Thread):
    def connect(self, host, port):
        self.sock.connect((host, port))

    def client(self, host, port, msg):
        sent = self.sock.send(msg)
        # print "Sent\n"
    
    # o método abaixo adiciona espaços em branco ao final do texto que será 
    # encriptado para que ele seja divisível por 16 bytes
    # isto porque o método encripta a mensagem usando um vetor de 16 bytes, 
    # ou seja, cada bloco da mensagem tem de ter 16 bytes.
    @staticmethod
    def padronizacao_mensagem(mensagem):
        while len(mensagem) % 16 != 0:
            mensagem = mensagem + " "
        return mensagem

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            #host = input("Digite o IP do servidor:\n>>")
            #port = int(input("Digite a porta de conexão ao servidor:\n>>"))
            host = '192.168.0.197'
            port = 5535
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

        # logo após receber a chave de criptografia e o vetor de inicializacao
        # criamos a varíavel de modo de criptografia e criamos o objeto que será
        # usado para criptografar e descriptografar a mensagem entre clientes
        global cifra
        print(output['c'])
        print(output['v'])
        cifra = Cipher(algorithms.AES(output['c']), modes.CBC(output['v']))

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

            # a função unidecode "normaliza" a mensagem para que a mesma não 
            # contenha acentos. Isso porquê quando o caracter ascii tem acentos
            # a função de encrypt logo abaixo, diz que a mensagem não está com
            # o tamanho múltiplo de 16, necessário para a criptografia.
            msg = unidecode.unidecode(msg)
            
            # aqui é chamada a função de padronização, para que a mensagem
            # tenha tamanho múltiplo de 16
            msg_padronizada = self.padronizacao_mensagem(msg)
            encryptor = cifra.encryptor()
            data = encryptor.update(str.encode(msg_padronizada)) + encryptor.finalize()

            #data = msg.encode()
            self.client(host, port, data)
        return (1)


if __name__ == '__main__':
    print("Iniciando Cliente")
    cli = Client()
    cli.start()