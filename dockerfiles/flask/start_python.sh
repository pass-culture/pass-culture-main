#!/bin/bash
set -x
cd /opt/services/flaskapp/src
pip install -r requirements.txt
sleep 3 # This leaves time for Postgres to create the DB
python -m trace -l app.py
