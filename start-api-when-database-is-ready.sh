#!/bin/bash
set -e

>&2 echo -e "\n\033[0;32mInstalling prerequisite\n"

apt update -y
apt-get install -y postgresql-client
apt-get install -y libpq-dev

>&2 echo -e "\n\033[0;32mInstalling application requirements\n"

pip install -e .
pip install -r ./requirements.txt;
python -m nltk.downloader punkt stopwords;

until psql $DATABASE_URL -c '\q'; do
  >&2 echo -e "\033[0;33mPostgres is unavailable - sleeping"
  sleep 1
done

>&2 echo -e "\n\033[0;32mPostgres is up - Install app\n"
python src/pcapi/install_database_extensions.py

>&2 echo -e "\n\033[0;32mPostgres is up - Running migration\n"
alembic upgrade head

>&2 echo -e "\n\033[0;32mMigrations have run - Starting the application\n"
while true; do python src/pcapi/app.py || continue; done;
