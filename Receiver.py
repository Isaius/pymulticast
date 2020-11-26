import socket
import struct
import sys
from time import sleep, time
from random import seed, random
import _thread

# Criando grupo multicast
multicast_group_tuple = ('224.2.2.3', 10000)
multicast_group = '224.2.2.3'
server_address = ('', 10001)
server_address2 = ('', 10000)

# Criando socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_address)

# Criando socket do grupo multicast
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind(server_address2)

group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# CONSTANTES DE TEMPO EM SEGUNDOS
HEARTBEAT_BASE_INTERVAL = 2
HEARTBEAT_MAX_INTERVAL = HEARTBEAT_BASE_INTERVAL + 1
CLEAR_ONLINE_INTERVAL = 4
WAIT_FOR_CLEAR = 3

# Vetor de servidores disponíveis
online = []

# Tempo do último heartbeat
last_hb = 0

# Contador de heartbeats
hb_count = 0

# ID do servidor
receiver_id = 0

# Thread para limpar o vetor de servidores disponíveis
def clear_online():
    while True:
        sleep(CLEAR_ONLINE_INTERVAL)
        global online
        online = []

# Thread para emitir heartbeats
def heartbeat_emmiter(thread_name, base_sleep):
    global receiver_id, last_hb, hb_count

    while True:
        # Definindo ID de servidor
        if receiver_id == 0:
            print("I was just born, waiting for mates")
            sleep(HEARTBEAT_MAX_INTERVAL)
            # Caso seja único servidor no grupo
            if len(online) == 0:
                print("I must be the number 1")
                receiver_id = 1
                continue
            print("Mates are:", online)
            online.sort()
            receiver_id = len(online)+1
            # Caso contrário definir ID como o primeiro disponível
            for i in range(len(online)):
                print(i, ":", online[i])
                if int(online[i]) != i+1:
                    receiver_id = i+1
                    break
            print("So I am ", receiver_id)

        seed(time())
        # Acréscimo aleatório de 0 a 1 no intervalo de heartbeat
        sleep(base_sleep + random())
        print('{}: Receiver {} sending heartbeat'.format(thread_name, receiver_id))
        heartbeat = 'HEY:' + str(receiver_id)

        # Checando por travamentos no programa
        print("Heartbeat!", hb_count)
        if hb_count > 0:
            diff = time() % 60 - last_hb
            print("Diff:", diff)

        sock2.sendto(heartbeat.encode(), multicast_group_tuple)
        last_hb = time() % 60
        hb_count += 1

# Thread para escutar heartbeats
def heartbeat_listener():
    while True:
        data, address = sock2.recvfrom(1024)

        msg = data.decode()

        if(msg.find("HEY") >= 0):
            data = msg.split(":")
            heartbeat_id = int(data[1])

            if(heartbeat_id not in online):
                online.append(heartbeat_id)

            print(online)


_thread.start_new_thread(clear_online, ())
_thread.start_new_thread(heartbeat_emmiter, ('HB Emmiter', HEARTBEAT_BASE_INTERVAL))
_thread.start_new_thread(heartbeat_listener, ())

# Responder cliente
while True:
    data, address = sock.recvfrom(1024)

    msg = data.decode()

    if(msg.find("HEY") < 0):
        print(msg)
        if(len(online) == 0):
            sleep(WAIT_FOR_CLEAR)
        
        online.sort()
        print(online)
        print("Selected is {}".format(online[0]))
        print(msg)
        print("{} == {}".format(receiver_id, online[0]))

        if(str(receiver_id) == str(online[0])):
            print("its me")
            result = str(eval(msg))
            sock.sendto(result.encode(), address)