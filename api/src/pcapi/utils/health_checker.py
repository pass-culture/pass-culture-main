import logging

from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def check_database_connection() -> bool:
    database_working = False
    try:
        db.session.query(User).limit(1).all()
        database_working = True
    except Exception as exc:
        logger.critical("Could not query database: %s", exc)

    return database_working


def read_version_from_file() -> str:
    with open("version.txt", "r", encoding="utf-8") as content_file:
        output = content_file.read()
    return output
