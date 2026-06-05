#!/usr/bin/env bash
set -e
echo "Waiting for database..."
python - <<'PY'
import os, time, sys
if os.getenv("POSTGRES_DB"):
    import socket
    host, port = os.getenv("POSTGRES_HOST","db"), int(os.getenv("POSTGRES_PORT","5432"))
    for _ in range(30):
        try:
            socket.create_connection((host, port), timeout=2).close(); break
        except OSError:
            time.sleep(1)
    else:
        print("DB not reachable"); sys.exit(1)
PY
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec "$@"
