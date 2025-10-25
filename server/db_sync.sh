#!/bin/sh
set -e

LAST_HASH=""

while true; do
  sleep 300  # 5 minutes

  if [ -f /app/db.sqlite3 ]; then
    CURRENT_HASH=$(md5sum /app/db.sqlite3 | awk '{ print $1 }')

    if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
      echo "Database changed, uploading..."
      gsutil cp /app/db.sqlite3 gs://$DB_BUCKET/db.sqlite3
      LAST_HASH=$CURRENT_HASH
    else
      echo "No changes detected, skipping upload."
    fi
  fi
done