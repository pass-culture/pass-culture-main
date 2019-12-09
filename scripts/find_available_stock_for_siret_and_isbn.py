from connectors.api_titelive_stocks import get_titelive_stocks, ApiTiteLiveException


def find_available_stock_for_siret_and_isbn(siret: str, isbn: str) -> int:
    last_seen_isbn = ''
    has_data_to_check = True

    while has_data_to_check:
        try:
            data = get_titelive_stocks(siret, last_seen_isbn)
        except ApiTiteLiveException:
            print("ISBN not found in TiteLive API")
            return -1

        for book_info in data['stocks']:
            if book_info['ref'] == isbn:
                return book_info['available']
            last_seen_isbn = book_info['ref']

    return 0
