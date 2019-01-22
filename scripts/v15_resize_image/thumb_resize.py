""" thumbs_resize """
import io

from PIL import Image
import requests

from utils.object_storage import store_public_object
from utils.storage_utils import do_list_content


def resize_all_images_from_object_storage():
    storage_name = 'storage-pc'
    objects_url = do_list_content(storage_name)
    for index, url in enumerate(objects_url):
        response = requests.get(url)
        thumb = response.content
        thumb_bytes = io.BytesIO(thumb)
        img = Image.open(thumb_bytes)
        print(img.format)
        if img.format != 'JPEG':
            print("%s %s %s" % (img.format, url, len(thumb) % 1000))
            continue
        end_of_jpeg_content = thumb.find(b'\xFF\xD9') + 1
        image_path = ('/').join(url.split('/')[-2:])
        new_content = thumb[:end_of_jpeg_content + 1]
        print(image_path)
        store_public_object(storage_name,
                            image_path,
                            new_content,
                            'image/jpeg')


def get_all_png_urls():
    storage_name = 'storage-pc'
    objects_url = do_list_content(storage_name)
    for index, url in enumerate(objects_url):
        response = requests.get(url)
        thumb = response.content
        thumb_bytes = io.BytesIO(thumb)
        img = Image.open(thumb_bytes)
        if img.format != 'JPEG':
            print("%s %s %s" % (img.format, url, len(thumb) % 1000))


resize_all_images_from_object_storage()