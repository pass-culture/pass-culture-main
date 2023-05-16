import logging
import os
from time import sleep
from flask import Flask, request, send_file, abort, make_response
from flask_cors import CORS
from google.appengine.api import wrap_wsgi_app, images
from io import BytesIO
from urllib.request import urlopen
import urllib

# Uncomment if you need to debug
# try:
#   import googleclouddebugger
#   googleclouddebugger.enable(
#     breakpoint_enable_canary=False
#   )
# except ImportError:
#   pass

app = Flask(__name__)
CORS(app)
app.wsgi_app = wrap_wsgi_app(app.wsgi_app)
logging.basicConfig(level = logging.INFO)

def get_mime_type(stream) -> str:
    data = stream.read(4)
    stream.seek(0)
    if data[:2] == b'\xff\xd8':
        return "image/jpeg"
    if data[:4] == b'\x89PNG':  
        return "image/png"
    return None

@app.route('/')
def root():
    filename = request.args.get("filename")
    size = request.args.get("size", type=int)

    if not filename:
        abort(404)

    blobstore_filename = '/gs/{}'.format(filename)
    serving_url = ""
    for cpt in range(1, 4):
        try:
            serving_url =   images.get_serving_url(blob_key=None, filename=blobstore_filename)
        except (images.Error, urllib.error.URLError):
            logging.error("Unable to get %s retry %s", blobstore_filename, cpt)
            sleep(1)
        else:
            break
    else:
        raise Exception(f"Unable to get serving url {blobstore_filename}")


    if size:
        url = '{}=s{}'.format(serving_url, size)
    else:
        url = serving_url

    logging.debug("Get bytes image from url %s", url)
    image_data = BytesIO(urlopen(url=url, timeout=5).read())
    mime_type = get_mime_type(image_data)
    if not mime_type:
        logging.error("Unable to determine MIME type of %s",filename)
        mime_type = "application/octet-stream"
    response = make_response(
        send_file(
            image_data,
            download_name=os.path.basename(filename),
            mimetype=mime_type
            )
        )
    # cache control header set, to work with Google cache cdn
    response.headers['Cache-Control'] = 'public, max-age=86400' # 1 day

    return response
