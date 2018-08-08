""" health_checker """
from models.user import User
import Exception


def check_database_connection():
    database_working = False
    try:
        User.query.limit(1).all()
        database_working = True
    except Exception as e:
        output = str(e)

    return database_working, output