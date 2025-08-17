import socket, time

PORT = 5012
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))
print('Server on port ' + str(PORT))

idle_start = time.time() #for timeout
players   = {}
used_nums = set()
need_size = None
round_no  = 0

def send(msg, addr): #send to one user
    sock.sendto(msg.encode(), addr)

def broadcast(msg):#send to all users
    for a in players:
        send(msg, a)

def active_players(): #count active players
    count = 0
    for p in players.values():
        if p['active']:
            count += 1
    return count

while True:
    sock.settimeout(0.2)
    try:
        data, x = sock.recvfrom(1024) # receive data
    except socket.timeout:
        data = None
    
    if time.time() - idle_start > 60: #stop after 60s (afk)
        print('Server stopped (afk for 60s)')
        break


    if data: #handle one datagram'
        idle_start = time.time() #to reset timer
        words = data.decode().strip().split() #split
        tag   = words[0]

        if tag == 'JOIN': # first player joins
            name = words[1] if len(words) > 1 else x[0] + ':' + str(x[1])
            players[x] = {'name': name, 'active': False, 'num': None}
            if need_size is None and len(players) == 1:
                send('Lobsize number of players to start game 2-20', x)
            else:
                broadcast(name + ' has joined the game')

        elif tag == 'SIZE' and need_size is None and x in players:
            size = int(words[1])
            if 2 <= size <= 20: # validate size
                need_size = size
                chooser_name = players[x]['name']
                broadcast(chooser_name + ' chose lobby size ' + str(need_size))
            else:
                send('error size must be 2-20', x)

        elif tag == 'NUM' and x in players and players[x]['active']:
            players[x]['num'] = int(words[1])# assume 1-100


    if need_size is None or len(players) < need_size:
        continue

    if all(not p['active'] for p in players.values()):
        for p in players.values():
            p['active'] = True
            p['num']    = None
        round_no = 1
        broadcast('Game starts!')
        broadcast('Round ' + str(round_no) + ': pick number 1-100')
        continue

    replied = 0 # count replies
    for p in players.values():
        if p['active'] and p['num'] is not None:
            replied += 1
    if replied == active_players():
        dupes  = {}
        losers = []

        for addr, p in players.items():# group dupes
            if p['active']:
                n = p['num']
                if n not in dupes:
                    dupes[n] = [addr]
                else:
                    dupes[n].append(addr)

        for addr, p in list(players.items()):# eliminate losers
            if p['active']:
                n = p['num']
                if n in used_nums or len(dupes[n]) > 1:
                    send('Out', addr)
                    losers.append(addr)
                    print('- ' + p['name'] + ' out (num=' + str(n) + ')')
                else:
                    used_nums.add(n)

        for addr in losers:
            players.pop(addr)

        for p in players.values():# let late joiners in next round
            p['active'] = True
            p['num']    = None

        alive = [p for p in players.values() if p['active']]
        if len(alive) == 1:
            broadcast('Win ' + alive[0]['name'])
            break
        if len(used_nums) == 100:
            broadcast('Win all')
            break

        round_no += 1
        broadcast('Players ' + str(len(alive)) +
                   ' unused ' + str(100 - len(used_nums)))
        broadcast('Round ' + str(round_no) + ': pick number 1-100')

print('Server stopped')
