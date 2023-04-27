from flask_wtf import FlaskForm
import wtforms


class EmptyForm(FlaskForm):
    pass


class BatchEmptyForm(FlaskForm):
    object_ids = wtforms.HiddenField("Identifiants à traiter")
