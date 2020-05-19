#!/bin/sh
# start-api-when-database-is-ready.sh

set -e
set -x;

apt-get install -y postgresql-client

>&2 echo "\n\e[32mInstalling requirements\n"
pip install -r ./requirements.txt;
python -m nltk.downloader punkt stopwords;

until psql $DATABASE_URL -c '\q'; do
  >&2 echo "\e[33mPostgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "\n\e[32mPostgres is up - Install app\n"
python install_database_extensions.py

>&2 echo "\n\e[32mPostgres is up - Running migration\n"
PYTHONPATH=. alembic upgrade head

>&2 echo "\n\e[32mMigrations has ran - Starting the application\n"
while true; do python app.py; done;
