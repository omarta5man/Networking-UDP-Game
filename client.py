import socket, threading, sys

SERVER = ('127.0.0.1', 5012)
name   = input('your name: ').strip()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(('Join ' + name).encode(), SERVER) # send packet

def listen():# listen for messags from server
    while True:
        txt, _ = sock.recvfrom(1024)
        msg = txt.decode().strip()

        if msg.startswith('Lobsize'):
            #first client picks lobby size
            while True:
                try:
                    size = int(input('number of players 2-20: '))
                except ValueError:
                    size = 0
                if 2 <= size <= 20:
                    break
                print('error: size cant be ' + str(size))
            sock.sendto(('Size ' + str(size)).encode(), SERVER)

        elif msg.startswith('Round'):
            print(msg)
            try:
                n = int(input('pick 1-100: '))
            except ValueError:
                n = 0
            sock.sendto(('Num ' + str(n)).encode(), SERVER)

        elif msg == 'Out':
            print('eliminated')
            sys.exit()

        elif msg.startswith('Win'):
            if ('all' in msg) or (name in msg):
                print('you win')
            else:
                print(msg)
            sys.exit()

        else:
            print(msg)

threading.Thread(target=listen, daemon=True).start()

try:
    while True:
        pass
except KeyboardInterrupt:
    sock.close()
    sys.exit()
