""" health_check """
from flask import current_app as app, jsonify

from utils.health_checker import check_database_connection


@app.route('/health', methods=['GET'])
def health():
    database_working, output = check_database_connection()
    return_code = 200 if database_working else 500
    return jsonify(output), return_code
