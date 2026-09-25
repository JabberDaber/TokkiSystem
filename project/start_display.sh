#!/bin/bash

PROJECT="/home/bush177/project"
cd "$PROJECT" || exit 1

python_pid=""

stop_display() {
    trap - TERM INT
    if [ -n "$python_pid" ]; then
        kill -TERM "$python_pid" 2>/dev/null
        wait "$python_pid" 2>/dev/null
    fi
    exit 0
}

trap stop_display TERM INT

while true; do
    /usr/bin/python3 "$PROJECT/main.py" >> "$PROJECT/display.log" 2>&1 &
    python_pid=$!
    wait "$python_pid" 2>/dev/null
    python_pid=""

    sleep 2 &
    wait $! 2>/dev/null
done
