#!/bin/bash
set -x
cd /opt/services/flaskapp/src
pip install -r requirements.txt
python app.py
