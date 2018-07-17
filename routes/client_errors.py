from pprint import pformat

from flask import current_app as app, request

from utils.mailing import send_dev_email


@app.route('/api/client_errors/store', methods=['POST'])
def post_error():
    data = request.get_json(force=True)
    if data is None:
        return "JSON data expected", 400
    else:
        send_dev_email("Client JS error",
                       "<html><body><pre>"
                       + pformat(data)
                       + "</pre></body></html>")

    return 'Email correctly send to dev with client error data'
