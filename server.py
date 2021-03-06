#!/usr/bin/env python
import time
import socket
import json
import re
import psutil
import platform
import sys
from subprocess import check_output
from threading import Thread
from wspy import websocket, Frame, OPCODE_TEXT


def osname():
    if platform.system() == 'Linux':
        distro, version, codename = platform.dist()
        name = 'Linux - %s %s' % (distro, version)

        if codename:
            name += ' (%s)' % codename

        return name

    return platform.platform()


def stats():
    # OS identification
    yield 'osname', osname()

    # Uptime
    yield 'uptime', time.time() - psutil.get_boot_time()

    # CPU temperature
    try:
        temps = []

        for line in check_output('sensors').split('\n'):
            m = re.match(r'^Core \d+:\s*\+(\d+\.\d+)', line)

            if m:
                temps.append(float(m.group(1)))

        assert len(temps) == psutil.NUM_CPUS
        yield 'temps', temps
    except:
        pass

    # CPU usage
    yield 'cpu_usage', round(psutil.cpu_percent(), 2)

    # Memory usage
    mem = psutil.phymem_usage()
    yield 'memory', (mem.used, mem.total)

    # Disk usage
    disk = psutil.disk_usage('/')
    yield 'disk', (disk.used, disk.total)


if __name__ == '__main__':
    clients = []

    def update():
        while True:
            if not clients:
                break

            status = Frame(OPCODE_TEXT, json.dumps(dict(stats())))

            for client in list(clients):
                try:
                    client.send(status)
                except socket.error:
                    print >>sys.stderr, 'Client disconnected'
                    clients.remove(client)

            time.sleep(1)

    server = websocket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', 8100))
    server.listen(5)

    t = Thread(target=update)
    t.daemon = True

    try:
        while True:
            try:
                sock, address = server.accept()
            except socket.error:
                continue

            print >>sys.stderr, 'Client connected at %s:%d' % address
            clients.append(sock)

            if not t.is_alive():
                t = Thread(target=update)
                t.daemon = True
                t.start()
    except KeyboardInterrupt:
        print >>sys.stderr, 'Stopping server'
    finally:
        server.close()
