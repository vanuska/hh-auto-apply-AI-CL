#!/bin/bash
set -e

# Запускаем Supervisor (Xvfb, VNC, noVNC)
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &

# Ждём, пока Xvfb запустится
sleep 3

# Устанавливаем DISPLAY
export DISPLAY=:99

# Запускаем основной скрипт (можно заменить на setup_tool.py или auto_apply.py)
if [ -z "$1" ]; then
    echo "Запуск setup_tool.py (интерактивный режим)"
    python3 /app/setup_tool.py
else
    echo "Запуск auto_apply.py с параметрами: $@"
    python3 /app/auto_apply.py "$@"
fi