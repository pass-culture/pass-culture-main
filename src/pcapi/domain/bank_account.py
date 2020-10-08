def format_raw_iban_and_bic(raw_data: str) -> str:
    if not raw_data:
        return None

    formatted_data = raw_data.upper()
    formatted_data = formatted_data.replace(' ', '')
    return formatted_data
