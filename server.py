#!/usr/bin/env python
import time
import socket
import json
import subprocess
import re
from threading import Thread
from twspy import websocket, TextMessage


def status_message():
    with open('/proc/uptime', 'r') as f:
        uptime, idletime = map(float, f.read().split(' '))

    temps = []

    for line in subprocess.check_output('sensors').split('\n'):
        m = re.match(r'^Core \d+:\s*\+(\d+\.\d+)', line)

        if m:
            temps.append(float(m.group(1)))

    cpu_idle = float(subprocess.check_output('mpstat').rsplit(' ', 1)[-1])

    data = {
        'uptime': uptime,
        'temps': temps,
        'cpu_usage': max(round(100 - cpu_idle, 2), 0)
    }

    return TextMessage(json.dumps(data))


if __name__ == '__main__':
    server = websocket()
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
            if len(clients):
                status = status_message()

                for client in list(clients):
                    try:
                        client.send(status.frame())
                    except socket.error:
                        print 'Client disconnected'
                        clients.remove(client)
            else:
                time.sleep(5)

            time.sleep(1)
    except KeyboardInterrupt:
        print 'Stopping server'
        server.close()
