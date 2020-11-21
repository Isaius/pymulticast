# socket_multicast_sender.py

import socket
import struct
import sys
from time import sleep

message = b'10 + 5 / 5'
#message = b'HEY:2'
multicast_group = ('224.2.2.3', 10000)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
sock.settimeout(0.2)

# Set the time-to-live for messages to 1 so they do not
# go past the local network segment.
ttl = struct.pack('b', 10)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:
    #inp = input('Insira a expressão')

    #message = inp.encode()

    # Send data to the multicast group
    print('sending {!r}'.format(message))
    sent = sock.sendto(message, multicast_group)
    sleep(10)
    # # Look for responses from all recipients
    # while True:
    #     print('waiting to receive')
    #     try:
    #         data, server = sock.recvfrom(16)
    #     except socket.timeout:
    #         print('timed out, no more responses')
    #         break
    #     else:
    #         print('received {!r} from {}'.format(
    #             data, server))

finally:
    print('closing socket')
    sock.close()