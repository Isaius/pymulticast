import socket
import struct
import re

# Constantes
MAX_RETRY_REQUEST = 3

# Global
retry_counter = -1

# Multicast e criação do socket
multicast_group = ('224.2.2.3', 10001)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Time Travel Limit de 1 para evitar que as mensagens saiam da rede local
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
sock.settimeout(3)

while True:
    expression = input("Digite a expressão desejada (ou 'e' para encerrar): ")

    if expression == 'e':
        break
    
    if re.search('[a-zA-Z]', expression):
        print("Expressão fornecida é inválida!")
        continue

    message = expression.encode()

    try:
        # Enviando a mensagem
        print('Enviando {!r}'.format(message))
        retry_counter = 0

        # Enviando mensagem e esperando resposta
        while True:
            sent = sock.sendto(message, multicast_group)
            print('Esperando receber')
            try:
                data, server = sock.recvfrom(1024)
            except socket.timeout:
                if retry_counter < MAX_RETRY_REQUEST:
                    retry_counter += 1
                    continue
                else:
                    print('Timeout, não houve resposta do servidor... :(')
                    break
            else:
                rsp = data.decode().split(':')
                print('Resposta do servidor {}: {}'.format(rsp[0], rsp[1]))
                break
    finally:
        pass

# Fechando o socket
sock.close()