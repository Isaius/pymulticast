import socket
import struct
import sys
import re
from time import sleep

# Multicast e criação do socket
multicast_group = ('224.2.2.3', 10001)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
sock.settimeout(10)

while True:
    expression = input("Digite a expressão desejada (ou 'e' para encerrar): ")

    if expression == 'e':
        break
    
    if re.search('[a-zA-Z]', expression):
        print("Expressão fornecida é inválida!")
        continue

    print(eval(expression))

    message = expression.encode()

    try:
        # Enviando a mensagem
        print('Enviando {!r}'.format(message))
        sent = sock.sendto(message, multicast_group)

        # Esperando a resposta
        while True:
            print('Esperando receber')
            try:
                data, server = sock.recvfrom(1024)
            except socket.timeout:
                print('Timeout, não houve resposta do servidor... :(')
                break
            else:
                print('Recebido {!r} do servidor {}'.format(data, server))
                break
    finally:
        pass

# Fechando o socket
sock.close()