import wtforms
from flask_wtf import FlaskForm


class EmptyForm(FlaskForm):
    pass


class BatchForm(FlaskForm):
    object_ids = wtforms.HiddenField("Identifiants à traiter")

    def validate_object_ids(self, object_ids: wtforms.HiddenField) -> wtforms.HiddenField:
        try:
            [int(id) for id in self.object_ids.data.split(",")]
        except ValueError:
            raise wtforms.validators.ValidationError("L'un des identifiants sélectionnés est invalide")
        return object_ids

    @property
    def object_ids_list(self) -> list[int]:
        object_ids_str = self.object_ids.data or ""
        object_ids_str_list = [id_str for id_str in object_ids_str.split(",") if id_str]
        return [int(id) for id in object_ids_str_list]
