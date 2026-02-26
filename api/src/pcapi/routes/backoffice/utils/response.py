from flask_wtf import FlaskForm
from markupsafe import Markup
from werkzeug.exceptions import Forbidden
from werkzeug.wrappers import Response as WerkzeugResponse


# perhaps one day we will be able to define it as str | tuple[str, int]
BackofficeResponse = str | tuple[str, int] | WerkzeugResponse | Forbidden


def build_form_error_msg(form: FlaskForm) -> str:
    error_msg = Markup("Les données envoyées comportent des erreurs.")
    for field in form:
        if field.errors:
            field_errors = []
            for error in field.errors:
                # form field errors are a dict, where keys are the failing field's name, and
                # the value is a list of all error messages
                if isinstance(error, dict):
                    field_errors += [
                        ", ".join(error_text for error_text in field_error_list) for field_error_list in error.values()
                    ]
                else:
                    field_errors.append(error)
            error_msg += Markup(" {label} : {errors} ;").format(
                label=field.label.text, errors=", ".join(error for error in field_errors)
            )
    return error_msg


def format_response_error_messages(errors: dict) -> list[str]:
    """
    Format unhandled errors. It's used in generate_error_response for htmx requests
    """
    lines = []
    for error_key, error_details in errors.items():
        for error_detail in error_details:
            lines.append(f"[{error_key}] {error_detail}")
    return lines
