import sentry_sdk


def tag_with_stream_name(stream_name: str) -> None:
    sentry_sdk.set_tag("stream_name", stream_name)
