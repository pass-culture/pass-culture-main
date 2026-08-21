import enum
import typing

from flask import flash

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.utils import advanced_search


OPERATORS_WITHOUT_VALUE = ("NOT_EXIST",)


class AdvancedSearchForm(utils.PCForm):
    form_field_configuration: typing.ClassVar[dict[str, dict[str, typing.Any]]]
    search_attributes: typing.ClassVar[type[enum.Enum]]
    search: fields.PCFieldListField

    def is_search_empty(self) -> bool:
        return all(self.is_sub_search_empty(sub_search) for sub_search in self.search.data)

    def get_advanced_search_errors(self) -> list[str]:
        errors = []

        for sub_search in self.search.data:
            if search_field := sub_search.get("search_field"):
                if self.is_sub_search_empty(sub_search):
                    try:
                        errors.append(f"Le filtre « {self.search_attributes[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")
                else:
                    operator = sub_search.get("operator")
                    if operator not in self.form_field_configuration.get(search_field, {}).get("operator", []):
                        try:
                            errors.append(
                                f"L'opérateur « {advanced_search.AdvancedSearchOperators[operator].value} » n'est pas supporté par le filtre {self.search_attributes[search_field].value}."
                            )
                        except KeyError:
                            errors.append(f"L'opérateur {operator} n'est pas supporté par le filtre {search_field}.")

        return errors

    def is_sub_search_empty(self, sub_search: dict[str, typing.Any]) -> bool:
        field_name = sub_search.get("search_field")
        operator = sub_search.get("operator")
        if field_name:
            field_attribute_name = self.form_field_configuration.get(field_name, {}).get("field", "")
            field_data = sub_search.get(field_attribute_name)
            if field_data not in (None, []):
                return False
            if operator in OPERATORS_WITHOUT_VALUE:
                return False

        return True

    def validate(self, extra_validators: dict | None = None) -> bool:
        if errors := self.get_advanced_search_errors():
            flash("\n".join(errors), "warning")
            return False

        return super().validate(extra_validators)
