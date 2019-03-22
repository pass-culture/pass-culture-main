from pprint import pformat

from flask import current_app as app, request, jsonify

from domain.admin_emails import send_dev_email
from utils.logger import logger
from utils.mailing import send_raw_email


@app.route('/api/client_errors/store', methods=['POST'])
def post_error():
    if not request.is_json:
        return jsonify('JSON data expected'), 400

    data = request.get_json(force=True)

    send_dev_email(
        'Client JS error',
        '<html><body><pre>%s</pre></body></html>' % pformat(data),
        send_raw_email
    )
    logger.error('[CLIENT ERROR] %s' % data)
    return jsonify('Email correctly sent to dev with client error data'), 200
