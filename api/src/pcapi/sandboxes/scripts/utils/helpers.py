def get_email(first_name: str, last_name: str, domain: str) -> str:
    return "{}.{}@{}".format(
        first_name.replace(" ", "").strip().lower(), last_name.replace(" ", "").strip().lower(), domain
    )
