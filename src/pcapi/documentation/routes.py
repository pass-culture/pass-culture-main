from flask import send_from_directory
from flask import current_app as app


@app.route('/api/doc', strict_slashes=False)
def api_documentation():
    return send_from_directory('static/documentation', 'index.html')


@app.route('/api/doc/<path:path>')
def static_files(path):
    if '.yaml' in path:
        return send_from_directory('documentation', path)

    return send_from_directory('static/documentation', path)
