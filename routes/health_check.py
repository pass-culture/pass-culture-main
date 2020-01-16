""" health_check """
from flask import current_app as app

from utils.health_checker import check_database_connection, read_version_from_file


@app.route('/health', methods=['GET'])
def health():
    database_working = check_database_connection()
    return_code = 200 if database_working else 500
    output = read_version_from_file()
    return output, return_code
