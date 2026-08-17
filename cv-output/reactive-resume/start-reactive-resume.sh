#!/usr/bin/env sh
set -eu

# Always run from the directory containing this script.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: Docker was not found. Install Docker Engine or Docker Desktop first." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not running, or the current user cannot access it." >&2
    echo "Start Docker or add your user to the docker group, then try again." >&2
    exit 1
fi

echo "[1/3] Preparing local secrets..."
if [ ! -f .env ]; then
    if command -v openssl >/dev/null 2>&1; then
        secret=$(openssl rand -base64 48 | tr -d '\n')
    elif [ -r /dev/urandom ] && command -v base64 >/dev/null 2>&1; then
        secret=$(dd if=/dev/urandom bs=48 count=1 2>/dev/null | base64 | tr -d '\n')
    else
        echo "ERROR: openssl or /dev/urandom with base64 is required to generate ENCRYPTION_SECRET." >&2
        exit 1
    fi
    umask 077
    printf 'ENCRYPTION_SECRET=%s\n' "$secret" > .env
    chmod 600 .env
    echo "Created private .env. Keep this file stable and do not commit it."
else
    echo ".env already exists; keeping the current encryption secret."
fi

echo "[2/3] Building and starting Reactive Resume..."
docker compose up -d --build

echo "[3/3] Waiting for the web application..."
attempts=0
while [ "$attempts" -lt 30 ]; do
    health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' reactive-resume-reactive-resume-1 2>/dev/null || true)
    if [ "$health" = "healthy" ]; then
        echo
        echo "Reactive Resume is ready: http://localhost:3000"
        exit 0
    fi
    attempts=$((attempts + 1))
    sleep 2
done

echo "WARNING: The containers started, but the application did not become healthy within 60 seconds." >&2
echo "Run: docker compose logs --tail 100 reactive-resume" >&2
exit 1
