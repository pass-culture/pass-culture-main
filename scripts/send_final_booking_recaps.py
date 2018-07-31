import traceback
from datetime import datetime
from pprint import pprint

from flask import current_app as app

from models.event_occurrence import EventOccurrence
from models.offer import Offer
from utils.mailing import send_booking_recap_emails

EventOccurrence = EventOccurrence
Offer = Offer


@app.manager.command
def send_final_booking_recaps():
    try:
        do_send_final_booking_recaps()
    except Exception as e:
        print('ERROR: '+str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def do_send_final_booking_recaps():
    for offer in Offer.query.outerjoin(EventOccurrence)\
                            .filter((datetime.utcnow() > Offer.bookingLimitDatetime) &
                                    ((Offer.eventOccurrenceId == None) |
                                     (EventOccurrence.beginningDatetime > datetime.utcnow())) &
                                    (Offer.bookingRecapSent == None)):
        print('Sending booking recap for ' + str(offer))
        send_booking_recap_emails(offer)
