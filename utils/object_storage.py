import os
from datetime import datetime
from pathlib import Path, PurePath

#import swiftclient
#
#user = 'account_name:username'  # TODO (get from secrets)
#key = 'your_api_key'
#
#def swift_con:
#    return swiftclient.Connection(user=user,
#                                  key=key,
#                                  authurl='https://objects.dreamhost.com/auth'
#                                 )

STORAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__)))\
              / '..' / 'static' / 'object_store_data'


def local_dir(bucket, id):
    if '/' in id:
        idFolders = PurePath(id).parent
    else:
        idFolders = ''
    return STORAGE_DIR / bucket / idFolders


def local_path(bucket, id):
    return local_dir(bucket, id) / PurePath(id).name


def store_public_object(bucket, id, blob, content_type):
    os.makedirs(local_dir(bucket, id), exist_ok=True)
    newFile = open(local_path(bucket, id), "wb")
    newFile.write(blob)
    newTypeFile = open(str(local_path(bucket, id))+".type", "w")
    newTypeFile.write(content_type)
#    swift_con().put_object(bucket,
#                           id,
#                           contents=blob,
#                           content_type=content_type)


def delete_public_object(bucket, id):
    lpath = local_path(bucket, id)
    if os.path.isfile(lpath):
        os.remove(lpath)


def get_public_object_date(bucket, id):
    lpath = local_path(bucket, id)
    if not os.path.isfile(lpath):
        return None
    return datetime.fromtimestamp(os.path.getmtime(lpath))
