from subprocess import Popen, PIPE
import os
from pathlib import Path


def pc_send_final_booking_recaps():
    print ("Cron:send_final_booking_recaps")
    pc_file = Path(os.path.dirname(os.path.realpath(__file__))) / 'pc.py'
    process = Popen(["python", pc_file, "send_final_booking_recaps"], stdout=PIPE)
    print(process.communicate())


if __name__ == '__main__':
    from apscheduler.schedulers.blocking import BlockingScheduler
    scheduler = BlockingScheduler()

    scheduler.add_job(pc_send_final_booking_recaps, 'cron', id='send_final_booking_recaps', minute='*/1')

scheduler.start()