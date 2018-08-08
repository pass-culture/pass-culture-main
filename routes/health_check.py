""" health_check """
from flask import current_app as app, jsonify

from utils.health_checker import check_database_connection


@app.route('/health', methods=['GET'])
def health():
    result = check_database_connection()
    return_code = 200 if result[0] else 500
    return jsonify(result[1]), return_code
