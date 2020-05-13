import re

from utils.config import API_URL, ENV


def check_origin_header_validity(header, endpoint, path):
    endpoint_exceptions = _get_endpoint_exceptions()

    if endpoint in endpoint_exceptions \
            or 'back-office' in path:
        return True

    if not header:
        return False

    white_list = _get_origin_header_whitelist()
    combined_white_list = "(" + ")|(".join(white_list) + ")"
    return re.match(combined_white_list, header) is not None


def _get_origin_header_whitelist():
    valid_urls = []
    if ENV == 'development':
        return [
            'http://localhost:3000',
            'http://localhost',
            'https://localhost',
            'localhost',
            'https://localhost:3000',
            'https://localhost:5000',
            'localhost:3000',
            'http://localhost:3001',
            'https://localhost:3001',
            'localhost:3001'
        ]
    # Handle migration to Scalingo
    elif ENV == 'testing':
        valid_urls = [
            'https://[.a-zA-Z-]+.passculture.app',
            'https://app-passculture-testing.scalingo.io',
            'https://passculture-team.netlify.com',
            'http://localhost:3000',
            'http://localhost',
            'https://localhost',
            'localhost',
            'https://localhost:3000',
            'localhost:3000',
            'http://localhost:3001',
            'https://localhost:3001',
            'localhost:3001'
        ]
    valid_urls.extend(_get_origin_header_whitelist_for_non_dev_environments(API_URL))
    return valid_urls


def _get_endpoint_exceptions():
    return ['patch_booking_by_token', 'get_booking_by_token', 'send_storage_file',
            'validate_offerer_attachment', 'validate_venue', 'validate_new_offerer',
            'get_bookings_csv',
            'list_features', 'show_dashboard_page', 'get_users_stats', ''
            'patch_booking_use_by_token',
            'get_booking_by_token_v2',
            'patch_booking_keep_by_token',
            'api_documentation',
            'static_files',
            'health_api',
            'health_database',
            'update_offerer_demarches_simplifiees_application',
            'update_venue_demarches_simplifiees_application'
            ]


def _get_origin_header_whitelist_for_non_dev_environments(api_url):
    url_variations = [api_url, api_url.replace('https', 'http'), api_url.replace('https://', '')]
    valid_urls = []
    for url in url_variations:
        valid_urls.append(url.replace('backend', 'pro'))
        valid_urls.append(url.replace('backend', 'app'))
        valid_urls.append(url.replace('backend', 'team'))

    return valid_urls
