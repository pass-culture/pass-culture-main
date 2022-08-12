import wtforms.fields as wtf_fields

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

    def __init__(self, *args, size=None, **kwargs):  # type: ignore [no-untyped-def]
        super().__init__(*args, **kwargs)
        self.flattened_choices = {option[0] for group in kwargs["choices"] for option in group[1]}
        self.size = size # type: ignore [no-untyped-def]

    def pre_validate(self, form):  # type: ignore [no-untyped-def]
        if self.data:
            invalid = set(self.data) - self.flattened_choices
            if invalid:
                raise ValueError("Les choix suivants ne sont pas valides : %s" % ", ".join(invalid))
