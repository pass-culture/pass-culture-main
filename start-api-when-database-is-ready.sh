#!/bin/bash

>&2 echo -e "\n\033[0;32mInstalling prerequisite\n"

apt update
apt-get install -y postgresql-client
apt-get install -y libpq-dev

>&2 echo -e "\n\033[0;32mInstalling application requirements\n"

pip install -r ./requirements.txt;
python -m nltk.downloader punkt stopwords;

until psql $DATABASE_URL -c '\q'; do
  >&2 echo -e "\033[0;33mPostgres is unavailable - sleeping"
  sleep 1
done

>&2 echo -e "\n\033[0;32mPostgres is up - Install app\n"
python install_database_extensions.py

>&2 echo -e "\n\033[0;32mPostgres is up - Running migration\n"
alembic upgrade head

>&2 echo -e "\n\033[0;32mMigrations has ran - Starting the application\n"
while true; do python app.py || continue; done;
