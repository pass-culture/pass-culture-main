from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.utils.logger import logger


def check_database_connection() -> bool:
    database_working = False
    try:
        UserSQLEntity.query.limit(1).all()
        database_working = True
    except Exception as e:
        logger.critical(str(e))

    return database_working


def read_version_from_file() -> str:
    with open("version.txt", "r") as content_file:
        output = content_file.read()
    return output
