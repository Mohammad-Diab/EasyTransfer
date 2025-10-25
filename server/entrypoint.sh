#!/bin/sh
set -e

gsutil cp gs://$DB_BUCKET/db.sqlite3 /app/db.sqlite3 || echo "No DB found, creating new one"

/app/db_sync.sh &

gunicorn main:app --bind 0.0.0.0:$PORT &

PID=$!

trap "echo 'Uploading DB before exit...'; gsutil cp /app/db.sqlite3 gs://$DB_BUCKET/db.sqlite3; exit 0" TERM INT

wait $PID