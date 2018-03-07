from flask import current_app as app, send_file
from utils.object_storage import local_path

print('LOCAL DEV MODE: Using disk based object storage')

@app.route('/storage/<bucketId>/<path:objectId>')
def send_storage_file(bucketId, objectId):
    print(local_path(bucketId, objectId))
    return send_file(local_path(bucketId, objectId))
