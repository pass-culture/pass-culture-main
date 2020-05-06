import os
import redis
from rq import Worker, Queue, Connection
from utils.config import REDIS_URL
from models.db import db
from flask import Flask
from sqlalchemy import orm




listen = ['default']
conn = redis.from_url(REDIS_URL)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
orm.configure_mappers()

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
