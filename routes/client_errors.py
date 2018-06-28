from flask import current_app as app, request
from utils.mailing import send_dev_email
from utils.rest import expect_json_data


@app.route('/client_errors', methods=['POST'])
@expect_json_data
def post_error():
    send_dev_email("Client JS error",
                   "<html><body><pre>"
                   + request.json()
                   + "</pre></body></html>")
