#!/bin/bash
set -x
cd /opt/services/flaskapp/src

pip install -r requirements.txt
python -m nltk.downloader punkt stopwords

function start_app_waiting_for_postgres {
  sleep 3
  while true; do
      python app.py
      sleep 2
  done
}

start_app_waiting_for_postgres
