import datetime
import typing


def _format_statement_value(value: typing.Any) -> typing.Any:
    if isinstance(value, int):
        return value

    if isinstance(value, (str, datetime.date, datetime.datetime, datetime.timedelta)):
        # Add quotes to make psql recognize the value as a string
        return f"'{str(value)}'"

    if isinstance(value, list):
        formatted_list = []
        for x in value:
            formatted_list.append(_format_statement_value(x))
        return formatted_list

    return str(value)


def format_sql_statement_params(params: typing.Optional[dict]) -> typing.Optional[dict]:
    if params is None:
        return None
    return {key: _format_statement_value(value) for key, value in params.items()}
