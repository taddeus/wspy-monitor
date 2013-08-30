#!/usr/bin/env python
import time
import socket
import json
import re
from subprocess import check_output
from threading import Thread
from twspy import websocket, Frame, OPCODE_TEXT, WebkitDeflateFrame


def stats():
    # Release
    dist, codename = check_output(['lsb_release', '-sdc']).rstrip().split('\n')
    yield 'release', '%s (%s)' % (dist, codename)

    # Uptime
    with open('/proc/uptime', 'r') as f:
        uptime, idletime = map(float, f.read().split(' '))
        yield 'uptime', uptime

    # CPU temperature
    try:
        temps = []

        for line in check_output('sensors').split('\n'):
            m = re.match(r'^Core \d+:\s*\+(\d+\.\d+)', line)

            if m:
                temps.append(float(m.group(1)))

        yield 'temps', temps
    except:
        pass

    # CPU usage
    with open('/proc/stat', 'r') as f:
        line = f.readlines()[0].rstrip().split()
        assert line[0] == 'cpu'
        numbers = map(int, line[1:])
        total = sum(numbers)
        idle = numbers[3]
        yield 'cpu_usage', round(float(total - idle) / total * 100, 2)

    # Memory usage
    with open('/proc/meminfo', 'r') as f:
        for line in f.readlines():
            if line.startswith('MemTotal'):
                assert line.endswith('kB\n')
                total = int(line.split()[1])
            elif line.startswith('MemFree'):
                assert line.endswith('kB\n')
                used = total - int(line.split()[1])
                yield 'memory', (used, total)
                break

    # Disk usage
    for line in check_output('df').split('\n'):
        parts = line.split()

        if parts[0].startswith('/dev/') and parts[5] == '/':
            used, avail = map(int, parts[2:4])
            yield 'disk', (used, used + avail)
            break

if __name__ == '__main__':
    server = websocket(extensions=[WebkitDeflateFrame()])
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', 12345))
    server.listen(5)
    clients = []

    def connect():
        while True:
            sock, address = server.accept()
            print 'Client connected at %s:%d' % address
            clients.append(sock)

    t = Thread(target=connect)
    t.daemon = True
    t.start()

    try:
        while True:
            if not clients:
                time.sleep(6)
                #time.sleep(.1)
                continue

            status = Frame(OPCODE_TEXT, json.dumps(dict(stats())))

            for client in list(clients):
                try:
                    client.send(status)
                except socket.error:
                    print 'Client disconnected'
                    clients.remove(client)

            time.sleep(1)
    except KeyboardInterrupt:
        print 'Stopping server'
        server.close()
