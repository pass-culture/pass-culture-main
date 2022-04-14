import typing

from flask_admin.form import rules


class HiddenField(rules.Field):
    """Use this in ``form_create_rules`` attributes so that labels of
    hidden fields are not displayed.

    Example:

        class MyView(ModelView):
            form_create_rules = [
              "name",
              HiddenRuleField("csrf"),
            ]
    """

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> str:
        return ""
