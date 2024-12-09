import enum
import typing

from wtforms.validators import Length
from wtforms.validators import Optional
from wtforms.validators import Regexp

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils


class SearchType(enum.Enum):
    ALL = "Tout"
    CHRONICLE_CONTENT = "Uniquement le contenu des chroniques"
    PRODUCT_NAME = "Uniquement le titre des offres"


class GetChronicleSearchForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("EAN, nom de l'offre, contenu des chroniques")

    search_type = fields.PCSelectField(
        "Type de recherche",
        choices=forms_utils.choices_from_enum(SearchType),
        default=SearchType.ALL.name,
        validators=(Optional(),),
    )

    date_range = fields.PCDateRangeField("Dates", validators=(Optional(),))
    page = fields.PCHiddenField("page", default="1", validators=(Optional(),))
    per_page = fields.PCSelectField(
        "Par page",
        choices=(("10", "10"), ("25", "25"), ("50", "50"), ("100", "100")),
        default="100",
        validators=(Optional(),),
    )


class UpdateContentForm(forms_utils.PCForm):

    def __init__(self, *args: typing.Any, content: str = "", **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        if content:
            self.content.data = content

    content = fields.PCTextareaField(
        "",  # the field name hides the text when scrolling on long chronicles.
        rows=15,
        validators=(Length(min=1),),
    )


class AttachProductForm(forms_utils.PCForm):
    ean = fields.PCStringField(
        "EAN", validators=[Regexp(r"^[0-9]{13}$", message="L'EAN doit être composé de 13 chiffres")]
    )


class CommentForm(forms_utils.PCForm):
    comment = fields.PCCommentField("Commentaire interne pour la chronique")
