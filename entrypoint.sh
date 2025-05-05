#!/usr/bin/env bash
set -e

# A short delay to let Postgres up.
sleep 5

# Migrations
python manage.py migrate --noinput
python manage.py seed_data

exec "$@"