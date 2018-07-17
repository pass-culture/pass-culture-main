from datetime import datetime
from flask import current_app as app
from pprint import pprint
import traceback

from utils.mailing import send_booking_recap_emails

EventOccurence = EventOccurence
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
    for offer in Offer.query.outerjoin(EventOccurence)\
                            .filter((datetime.utcnow() > Offer.bookingLimitDatetime) &
                                    ((Offer.eventOccurenceId == None) |
                                     (EventOccurence.beginningDatetime > datetime.utcnow())) &
                                    (Offer.bookingRecapSent == None)):
        print('Sending booking recap for ' + str(offer))
        send_booking_recap_emails(offer)
