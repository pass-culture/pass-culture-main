""" health_checker """
from models.user import User


def check_database_connection():
    database_working = False
    try:
        User.query.limit(1).all()
        database_working = True
        output = "ok"
    except Exception as e:
        logger.critical(str(e))
        output = "Database connection failed"

    return database_working, output
