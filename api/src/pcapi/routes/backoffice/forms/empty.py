from flask_wtf import FlaskForm
import wtforms


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
        return [int(id) for id in self.object_ids.data.split(",")]
