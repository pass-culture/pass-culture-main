from flask import send_from_directory
from flask import current_app as app


@app.route('/api/doc/<path:path>')
def api_documentation(path):
    return send_from_directory('static/documentation', path)
