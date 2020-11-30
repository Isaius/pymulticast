import socket
import struct
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

# IP do servidor
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

# Vetor de servidores vivos
alive = []
last_alive = []

# Vetor de servidores caídos
wanted = []

# Função da thread para limpar o vetor de servidores disponíveis
def clear_online():
    global online, alive, last_alive, wanted
    
    while True:
        sleep(CLEAR_ONLINE_INTERVAL)
        online = []
        
        # Limpando servidores ativos
        diff = list(set(last_alive) - set(alive))
        if ((receiver_id != 0 and all(x in alive for x in diff)) or hb_count < 2):
            print(receiver_id, ": We're good")
        else:
            wanted += diff
            print(receiver_id, ": We're wanted", wanted)
        print(receiver_id, ": Alive are", alive)
        last_alive = alive
        alive = []

def heartbeat_message():
    return "HEY:{}:{}".format(receiver_id, wanted)

# Thread para emitir heartbeats
def heartbeat_emmiter(thread_name, base_sleep):
    global receiver_id, last_hb, hb_count, wanted

    while True:
        # Definindo ID de servidor
        if receiver_id == 0:
            print(receiver_id, ": I was just born, waiting for mates")
            sleep(HEARTBEAT_MAX_INTERVAL)
            # Caso seja único servidor no grupo
            if len(online) == 0:
                print(receiver_id, ": I must be the number 1")
                receiver_id = 1
                continue
            # Caso contrário definir ID como o primeiro disponível
            print(receiver_id, ": Mates are:", online)
            online.sort()
            receiver_id = len(online)+1
            for i in range(len(online)):
                if int(online[i]) != i+1:
                    receiver_id = i+1
                    break
            print(receiver_id, ": So I am ", receiver_id)

        seed(time())
        # Acréscimo aleatório de 0 a 1 no intervalo de heartbeat
        sleep(base_sleep + random())
        
        print('{}: Receiver {} sending heartbeat'.format(thread_name, receiver_id))
        heartbeat = heartbeat_message()

        if receiver_id != 0:
            # Checando por travamentos no programa
            if wanted.__contains__(ip):
                receiver_id = 0
                hb_count = 0
                wanted.remove(ip)
                sock2.sendto(heartbeat_message().encode(), multicast_group_tuple)
                continue

            sock2.sendto(heartbeat.encode(), multicast_group_tuple)
            last_hb = time() % 60
            hb_count += 1

# Thread para escutar heartbeats
def heartbeat_listener():
    global wanted

    while True:
        data, address = sock2.recvfrom(1024)

        msg = data.decode()
        print(msg)

        if(msg.find("HEY") >= 0):
            data = msg.split(":")
            heartbeat_id = int(data[1])

            if(heartbeat_id != 0 and heartbeat_id not in online):
                online.append(heartbeat_id)

            if (address[0] not in alive):
                alive.append(address[0])
    
            rec_down = data[2][2:-2].split("', '")

            if set(wanted) != set(rec_down):
                wanted = rec_down
    
            print(receiver_id, ": Wanted are", wanted)

            print("online:", online)


_thread.start_new_thread(clear_online, ())
_thread.start_new_thread(heartbeat_emmiter, ('HB Emmiter', HEARTBEAT_BASE_INTERVAL))
_thread.start_new_thread(heartbeat_listener, ())

# Responder cliente
while True:
    data, address = sock.recvfrom(1024)

    msg = data.decode().split(':')
    print(msg[1])

    # se a lista online estiver vazia espera os heartbeats
    if len(online) <= 0:
        sleep(WAIT_FOR_CLEAR)

    online.sort()
    print(online)

    if(len(online) > 0 and str(receiver_id) == str(online[0])):
        result = str(eval(msg[1]))
        rsp = '{}:{}:{}'.format(receiver_id, result, msg[0])
        print(receiver_id, ": I am the sheriff now and I say: {}".format(result))
        
        sock.sendto(rsp.encode(), address)
 