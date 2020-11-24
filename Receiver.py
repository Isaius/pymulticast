# socket_multicast_receiver.py

import socket
import struct
import sys
from time import sleep, time
from random import seed, random
import _thread

multicast_group_tuple = ('224.2.2.3', 10000)
multicast_group = '224.2.2.3'
server_address = ('', 10000)
receiver_id = sys.argv[1]
online = []

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_ADD_MEMBERSHIP,
    mreq)

def clear_online():
    while True:
        sleep(3)
        global online
        online = []

def heartbeat_emmiter(thread_name, base_sleep):
    while True:
        seed(time())
        # set a sleep between 3 and 4 for diferent heartbeat times through the group
        sleep(base_sleep + random())
        print('{}: Receiver {} sending heartbeat'.format(thread_name, receiver_id))
        heartbeat = 'HEY:' + receiver_id
        sock.sendto(heartbeat.encode(), multicast_group_tuple)


_thread.start_new_thread(clear_online, ())
_thread.start_new_thread(heartbeat_emmiter, ('HB Emmiter', 3))

# Receive/respond loop
while True:
    data, address = sock.recvfrom(1024)

    msg = data.decode()
    
    if(msg.find("HEY") >= 0):
        data = msg.split(":")
        heartbeat_id = int(data[1])

        if(heartbeat_id not in online):
            online.append(heartbeat_id)

        print(online)
    else:
        if(len(online) == 0):
            sleep(1)
        
        online.sort()
        print(online)
        print("Selected is {}".format(online[0]))
        print(msg)
        print("{} == {}".format(receiver_id, online[0]))

        if(receiver_id == str(online[0])):
            print("its me")
            result = str(eval(msg))
            sock.sendto(result.encode(), address)