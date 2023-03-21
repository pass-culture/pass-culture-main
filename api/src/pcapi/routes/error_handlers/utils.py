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


def format_sql_statement_params(params: dict | None) -> dict | None:
    if params is None:
        return None
    return {key: _format_statement_value(value) for key, value in params.items()}


def generate_error_response(errors: dict, backoffice_template_name: str = "errors/generic.html") -> Response:
    if request.path.startswith("/backofficev3"):
        # If the error happens inside a turbo-frame, it's id is reused to insert the error in the correct place
        turbo_frame_id = request.headers.get("Turbo-Frame")
        content = render_template(backoffice_template_name, errors=errors, turbo_frame_id=turbo_frame_id)
        return make_response(content)

    return jsonify(errors)
