FROM postgres:10.1

RUN
    apt-get update
    apt-get install curl
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    pip install psycopg2-binary
    pip install pgcli