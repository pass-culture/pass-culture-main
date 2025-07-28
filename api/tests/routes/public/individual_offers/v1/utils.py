import typing
from datetime import datetime


KwargBaseTypes = bool | int | float | str | datetime
KwargInput = KwargBaseTypes | typing.Collection[KwargBaseTypes]


def assert_public_api_data_logs_have_been_recorded(caplog, api_key, **kwargs: KwargInput) -> None:
    """Assert that the expected information have been logged

    All expected information should be passed to `kwargs` except the two
    authenticated related fields: `api_key` and `provider_id` that are
    checked using the `api_key` input.
    """
    log_record = next(
        record
        for record in caplog.records
        if hasattr(record, "technical_message_id") and record.technical_message_id == "public_api.call"
    )

    public_api_extra_data = log_record.public_api
    assert public_api_extra_data == {
        "api_key": api_key.id,
        "provider_id": api_key.providerId,
        **kwargs,
    }
