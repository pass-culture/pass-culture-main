import typing

import wtforms.fields as wtf_fields
from wtforms.form import Form

from . import widgets


class SelectMultipleFieldWithOptgroups(wtf_fields.SelectMultipleField):
    """Display a <select> widget with <optgroup> tags.

    Choices should looke like this:

        [
            ("Mammal", [
              ("id-of-elephant", "Elephant"),
              ("id-of-kangaroo", "Kangaroo"),
            ]),
            ("Reptile", [
              ("id-of-snake", "Snake"),
            ]),
        ]

    Limitation: all options must be part of an optgroup.
    """

    widget = widgets.SelectWithOptgroups(multiple=True)

    def __init__(self, *args: typing.Any, size: int | None = None, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.flattened_choices = {option[0] for group in kwargs["choices"] for option in group[1]}
        self.size = size

    def pre_validate(self, form: Form) -> None:
        if self.data:
            invalid = set(self.data) - self.flattened_choices
            if invalid:
                raise ValueError("Les choix suivants ne sont pas valides : %s" % ", ".join(invalid))
