from flask import send_from_directory
from flask import current_app as app


@app.route('/api/doc')
def api_documentation_index():
    return send_from_directory('static/documentation', 'index.html')


@app.route('/api/doc/<path:path>')
def api_documentation(path):
    if '.json' in path:
        return send_from_directory('documentation', path)

    return send_from_directory('static/documentation', path)
