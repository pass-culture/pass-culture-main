from datetime import datetime


def make_transaction_label(date: datetime.date) -> str:
    month_and_year = date.strftime("%m-%Y")
    period = "1ère" if date.day < 15 else "2nde"
    return "pass Culture Pro - remboursement %s quinzaine %s" % (period, month_and_year)
