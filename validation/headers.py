from utils.config import API_URL, ENV


def check_origin_header_validity(header, endpoint):
    endpoint_exceptions = _get_endpoint_exceptions()
    if endpoint in endpoint_exceptions:
        return True
    white_list = _get_origin_header_whitelist()
    return header in white_list


def _get_origin_header_whitelist():
    if ENV == 'development':
        return [
            'http://localhost:3000',
            'https://localhost:3000',
            'localhost:3000',
            'http://localhost:3001',
            'https://localhost:3001',
            'localhost:3001'
        ]
    return _get_origin_header_whitelist_for_non_dev_environments(API_URL)


def _get_endpoint_exceptions():
    return ['patch_booking_by_token', 'get_booking_by_token']


def _get_origin_header_whitelist_for_non_dev_environments(api_url):
    url_variations = [api_url, api_url.replace('https', 'http'), api_url.replace('https://', '')]
    valid_urls = []
    for url in url_variations:
        valid_urls.append(url.replace('backend', 'pro'))
        valid_urls.append(url.replace('backend', 'app'))
    return valid_urls
