""" clock """
import os
from flask import Flask
from mailjet_rest import Client
from apscheduler.schedulers.blocking import BlockingScheduler

from models.db import db
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET
from subprocess import PIPE,Popen

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)


def pc_send_final_booking_recaps():
    print("Cron send_final_booking_recaps: START")
    with app.app_context():
        from scripts.send_final_booking_recaps import send_final_booking_recaps

        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')

        send_final_booking_recaps()

    print("Cron send_final_booking_recaps: END")


def pc_restore_database():
    print("Cron update database: START")
    if "TARGET_DATABASE" not in os.environ:
        print("Job cancelled : $TARGET_DATABASE is not set.")
        return

    print("Install dbclient for postgresql : start")
    command = 'dbclient-fetcher postgresql 10.4'
    p = Popen(command,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
    print(p.communicate())
    if p.returncode != 1:
        print("An error as occured during the backup process.")
        return
    print("Install dbclient for postgresql : done")

    print("Target database backup : start")
    command = 'pg_dump $TARGET_DATABASE -Fc -f /tmp/database.pgdump'
    p = Popen(command,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
    print("Target database backup : en cours")
    print(p.communicate())
    if p.returncode != 1:
        print("An error as occured during the backup process.")
        return
    print("Target database backup : done")

    print("Database restore : start")
    command = 'pg_restore -d $DATABASE_URL -c /tmp/database.pgdump'
    p = Popen(command,shell=False,stdin=PIPE,stdout=PIPE,stderr=PIPE)
    print(p.communicate())
    if p.returncode != 1:
        print("An error as occured during the restore process.")
        return
    print("Database restore : done")

    print("Cron send_final_booking_recaps: END")


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(pc_send_final_booking_recaps, 'cron', id='send_final_booking_recaps', minute='*/10')
    scheduler.add_job(pc_restore_database, 'cron', id='restore_database', minute='*/5') # day_of_week='mon')

    scheduler.start()
