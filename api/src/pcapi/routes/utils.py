import sentry_sdk


def tag_with_api_user_typology(api_user_typology: str) -> None:
    sentry_sdk.set_tag("api_user_typology", api_user_typology)
