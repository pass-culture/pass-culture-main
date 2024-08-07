import random
import typing

from flask_wtf import FlaskForm
from markupsafe import Markup

from pcapi.utils import email as email_utils


class PCForm(FlaskForm):
    def filter_email(self, raw_email: str | None) -> str:
        if not raw_email:
            return ""
        return email_utils.sanitize_email(raw_email)

    @property
    def raw_data(self) -> dict[str, typing.Any]:
        return {field.name: field.raw_data for field in self}


def random_hash() -> str:
    return format(random.getrandbits(128), "x")


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
