import traceback
from pprint import pprint

from flask import current_app as app

from domain.user_emails import send_final_booking_recap_email
from repository.stock_queries import find_stocks_of_finished_events_when_no_recap_sent
from utils.mailing import save_and_send


def send_final_booking_recaps():
    try:
        do_send_final_booking_recaps()
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def do_send_final_booking_recaps():
    for stock in find_stocks_of_finished_events_when_no_recap_sent():
        print('Sending booking recap for ' + str(stock))
        send_final_booking_recap_email(stock, save_and_send)
