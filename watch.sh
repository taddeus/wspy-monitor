#!/usr/bin/env sh

hash inotifywait || (echo "Install inotify-tools first"; exit 1)

make

while true; do
    inotifywait --quiet --exclude \.swp\$ --event moved_to,attrib,modify \
        *.coffee
    sleep 0.05s
    make
done
