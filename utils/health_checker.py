""" health_checker """
from models.user import User


def check_database_connection():
    database_working = False
    try:
        User.query.limit(1).all()
        database_working = True
        output = "ok"
    except Exception as e:
        output = str(e)

    return database_working, output
