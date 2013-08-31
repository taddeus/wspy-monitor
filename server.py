#!/usr/bin/env python
import time
import socket
import json
import re
import psutil
import platform
from subprocess import check_output
from threading import Thread
from wspy import websocket, Frame, OPCODE_TEXT, WebkitDeflateFrame


def osname():
    if platform.system() == 'Linux':
        distro, version, codename % platform.dist()
        name = 'Linux - %s %s' % (distro, version)

        if codename:
            name += ' (%s)' % codename

        return name

    #return '%s %s' % (platform.system(), platform.release())
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
    cpu = psutil.cpu_times()
    total = sum(cpu)
    yield 'cpu_usage', round(float(total - cpu.idle) / total * 100, 2)

    # Memory usage
    mem = psutil.phymem_usage()
    yield 'memory', (mem.used, mem.total)

    # Disk usage
    disk = psutil.disk_usage('/')
    yield 'disk', (disk.used, disk.total)


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
