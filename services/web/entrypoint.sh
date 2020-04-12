#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

#Drops the DB
python manage.py create_db
echo "db created"

#Should create a new admin
python manage.py seed_db
echo "db seeded"

exec "$@"