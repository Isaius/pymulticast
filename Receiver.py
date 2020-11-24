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
receiver_id = sys.argv[1]

# Vetor de servidores disponíveis
online = []

# Criando socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_address)

# Criando socket do grupo multicast
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind(server_address2)

group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Thread para limpar o vetor de servidores disponíveis
def clear_online():
    while True:
        sleep(4)
        global online
        online = []

# Thread para emitir heartbeats
def heartbeat_emmiter(thread_name, base_sleep):
    while True:
        seed(time())
        # set a sleep between 3 and 4 for diferent heartbeat times through the group
        sleep(base_sleep + random())
        print('{}: Receiver {} sending heartbeat'.format(thread_name, receiver_id))
        heartbeat = 'HEY:' + receiver_id
        sock2.sendto(heartbeat.encode(), multicast_group_tuple)

# Thread para escutar heartbeats dos servidores
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
_thread.start_new_thread(heartbeat_emmiter, ('HB Emmiter', 2))
_thread.start_new_thread(heartbeat_listener, ())

# Responder cliente
while True:
    data, address = sock.recvfrom(1024)

    msg = data.decode()

    if(msg.find("HEY") < 0):
        print(msg)
        if(len(online) == 0):
            sleep(3)
        
        online.sort()
        print(online)
        print("Selected is {}".format(online[0]))
        print(msg)
        print("{} == {}".format(receiver_id, online[0]))

        if(receiver_id == str(online[0])):
            print("its me")
            result = str(eval(msg))
            sock.sendto(result.encode(), address)