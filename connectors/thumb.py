import requests


def fetch_image(thumb_url: str, target_object: str) -> bytes:
    if not thumb_url[0:4] == 'http':
        raise ValueError('Invalid thumb URL for object %s : %s' % (target_object, thumb_url))

    response = requests.get(thumb_url)
    content_type = response.headers['Content-type']
    is_an_image = content_type.split('/')[0] == 'image'

    if response.status_code == 200 and is_an_image:
        return response.content
    else:
        raise ValueError(
            'Error downloading thumb for object %s from url %s (status_code : %s)'
            % (target_object, thumb_url, str(response.status_code)))
