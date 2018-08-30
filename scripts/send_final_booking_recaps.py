import traceback
from datetime import datetime
from pprint import pprint

from flask import current_app as app

from models.event_occurrence import EventOccurrence
from models.stock import Stock
from utils.mailing import send_final_booking_recap_email


@app.manager.command
def send_final_booking_recaps():
    try:
        do_send_final_booking_recaps()
    except Exception as e:
        print('ERROR: '+str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def do_send_final_booking_recaps():
    for stock in Stock.queryNotSoftDeleted().outerjoin(EventOccurrence)\
                            .filter((datetime.utcnow() > Stock.bookingLimitDatetime) &
                                    ((Stock.eventOccurrenceId == None) |
                                     (EventOccurrence.beginningDatetime > datetime.utcnow())) &
                                    (Stock.bookingRecapSent == None)):
        print('Sending booking recap for ' + str(stock))
        send_final_booking_recap_email(stock)
