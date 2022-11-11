from flask_wtf import FlaskForm

from . import fields


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour la structure")
