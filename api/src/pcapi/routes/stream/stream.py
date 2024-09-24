from flask_sse import sse

from pcapi.flask_app import app


# TODO: remove test route later
@app.route("/send")
def send_message():
    sse.publish({"message": "Hello!"}, type="greeting")
    return "Message sent!"
