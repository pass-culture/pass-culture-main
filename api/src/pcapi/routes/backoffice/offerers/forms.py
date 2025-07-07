import re
import typing

import sqlalchemy.orm as sa_orm
import wtforms
from flask_wtf import FlaskForm

from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.utils import get_regions_choices
from pcapi.utils import siren as siren_utils
from pcapi.utils import string as string_utils


TAG_NAME_REGEX = r"^[^\s]+$"
DIGITS_AND_WHITESPACES_REGEX = re.compile(r"^[\d\s]+$")


def _get_all_tags_query() -> sa_orm.Query:
    return (
        db.session.query(offerers_models.OffererTag)
        .order_by(offerers_models.OffererTag.label)
        .options(
            sa_orm.load_only(
                offerers_models.OffererTag.id, offerers_models.OffererTag.name, offerers_models.OffererTag.label
            )
        )
    )


def _get_validation_tags_query() -> sa_orm.Query:
    return (
        db.session.query(offerers_models.OffererTag)
        .join(offerers_models.OffererTagCategoryMapping)
        .join(offerers_models.OffererTagCategory)
        .filter(offerers_models.OffererTagCategory.name == "homologation")
        .order_by(offerers_models.OffererTag.label)
    )


class EditOffererForm(FlaskForm):
    tags = fields.PCQuerySelectMultipleField(
        "Tags",
        query_factory=_get_all_tags_query,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: tag.label or tag.name,
    )
    name = fields.PCStringField(
        "Nom de l'entité juridique",
        validators=(
            wtforms.validators.DataRequired("Le nom est obligatoire"),
            wtforms.validators.Length(max=140, message="doit contenir moins de %(max)d caractères"),
        ),
    )
    postal_address_autocomplete = fields.PcPostalAddressAutocomplete(
        "Adresse",
        street="street",
        city="city",
        # TODO: bdalbianco 5/5/2025 check if ban_id and inseecode are relevant here. If not, remove and fix tests
        ban_id=None,
        insee_code=None,
        postal_code="postal_code",
        latitude=None,
        longitude=None,
        required=True,
        has_reset=True,
        has_manual_editing=True,
        limit=10,
    )
    street = fields.PCOptHiddenField(
        "Adresse",
        validators=(wtforms.validators.Length(max=200, message="doit contenir moins de %(max)d caractères"),),
    )
    postal_code = fields.PCPostalCodeHiddenField("Code postal")
    city = fields.PCHiddenField(
        "Ville",
        validators=(
            wtforms.validators.Length(min=1, max=50, message="doit contenir entre %(min)d et %(max)d caractères"),
        ),
    )


class SuspendOffererForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne optionnel")


class FraudForm(FlaskForm):
    confidence_level = fields.PCSelectField(
        "Validation des offres",
        choices=utils.choices_from_enum(
            offerers_models.OffererConfidenceLevel, formatter=filters.format_confidence_level
        ),
        default_text="Suivre les règles",
        validators=(wtforms.validators.Optional(""),),
    )
    comment = fields.PCOptCommentField("Commentaire visible uniquement par l'équipe Fraude et Conformité")

    def filter_confidence_level(self, raw_confidence_level: str | None) -> str | None:
        if not raw_confidence_level:
            return None  # instead of empty string
        return raw_confidence_level


class OffererValidationListForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Nom, SIREN, code postal, dép., ville, email, nom de compte pro, ID DMS CB")
    regions = fields.PCSelectMultipleField("Régions", choices=get_regions_choices())
    tags = fields.PCQuerySelectMultipleField(
        "Tags",
        query_factory=_get_all_tags_query,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: tag.label or tag.name,
    )
    status = fields.PCSelectMultipleField(
        "États",
        choices=utils.choices_from_enum(
            ValidationStatus, formatter=filters.format_validation_status, exclude_opts=(ValidationStatus.DELETED,)
        ),
    )
    ae_documents_received = fields.PCSelectMultipleField(
        "Documents reçus",
        choices=[("yes", "Oui"), ("no", "Non")],
    )
    instructors = fields.PCTomSelectField(
        "Dernier instructeur",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_bo_users",
    )
    dms_adage_status = fields.PCSelectMultipleField(
        "États du dossier DMS ADAGE",
        choices=utils.choices_from_enum(GraphQLApplicationStates, filters.format_dms_application_status),
    )
    from_date = fields.PCDateField("Demande à partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Demande jusqu'au", validators=(wtforms.validators.Optional(),))

    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (10, "Afficher 10 résultats maximum"),
            (25, "Afficher 25 résultats maximum"),
            (50, "Afficher 50 résultats maximum"),
            (100, "Afficher 100 résultats maximum"),
        ),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    order = wtforms.HiddenField(
        "order", default="desc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )
    sort = wtforms.HiddenField(
        "sort",
        default="dateCreated",
        validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("dateCreated",))),
    )

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            # Remove spaces from SIREN, IDs, postal code
            if DIGITS_AND_WHITESPACES_REGEX.match(q.data):
                q.data = re.sub(r"\s+", "", q.data)
            if string_utils.is_numeric(q.data) and len(q.data) not in (
                2,  # department
                3,  # department
                5,  # postal code
                siren_utils.RID7_LENGTH,
                siren_utils.SIREN_LENGTH,
                12,  # DMS
            ):
                raise wtforms.validators.ValidationError(
                    "Le nombre de chiffres ne correspond pas à un SIREN, RID7, code postal, département ou ID DMS CB"
                )
        return q


class UserOffererValidationListForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField(
        "Nom d'entité juridique, SIREN, code postal, département, ville, email, nom de compte pro"
    )
    regions = fields.PCSelectMultipleField("Régions", choices=get_regions_choices())
    tags = fields.PCQuerySelectMultipleField(
        "Tags",
        query_factory=_get_validation_tags_query,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: tag.label or tag.name,
    )
    status = fields.PCSelectMultipleField(
        "États de la demande de rattachement",
        choices=utils.choices_from_enum(
            ValidationStatus, formatter=filters.format_validation_status, exclude_opts=(ValidationStatus.CLOSED,)
        ),
    )
    instructors = fields.PCTomSelectField(
        "Dernier instructeur",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_bo_users",
    )
    offerer_status = fields.PCSelectMultipleField(
        "États de l'entité juridique",
        choices=utils.choices_from_enum(
            ValidationStatus, formatter=filters.format_validation_status, exclude_opts=(ValidationStatus.DELETED,)
        ),
    )
    from_date = fields.PCDateField("Demande à partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Demande jusqu'au", validators=(wtforms.validators.Optional(),))

    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (10, "Afficher 10 résultats maximum"),
            (25, "Afficher 25 résultats maximum"),
            (50, "Afficher 50 résultats maximum"),
            (100, "Afficher 100 résultats maximum"),
        ),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )
    order = wtforms.HiddenField(
        "order", default="desc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )
    sort = wtforms.HiddenField(
        "sort",
        default="id",
        validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("id", "dateCreated"))),
    )

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            # Remove spaces from SIREN, IDs, postal code
            if DIGITS_AND_WHITESPACES_REGEX.match(q.data):
                q.data = re.sub(r"\s+", "", q.data)
            if string_utils.is_numeric(q.data) and len(q.data) not in (
                2,
                3,
                5,
                siren_utils.RID7_LENGTH,
                siren_utils.SIREN_LENGTH,
            ):
                raise wtforms.validators.ValidationError(
                    "Le nombre de chiffres ne correspond pas à un SIREN, RID7, code postal ou département"
                )
        return q


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour l'entité juridique")


class OptionalCommentForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne (optionnel)")


class BatchOptionalCommentForm(empty_forms.BatchForm, OptionalCommentForm):
    pass


class OffererValidationForm(OptionalCommentForm):
    review_all_offers = fields.PCSwitchBooleanField("Revue manuelle de toutes les offres")


class BatchOffererValidationForm(empty_forms.BatchForm, OffererValidationForm):
    pass


class OffererRejectionForm(OptionalCommentForm):
    rejection_reason = fields.PCSelectField(
        "Raison du rejet",
        choices=utils.choices_from_enum(
            offerers_models.OffererRejectionReason, filters.format_offerer_rejection_reason
        ),
    )


class BatchOffererRejectionForm(empty_forms.BatchForm, OffererRejectionForm):
    pass


class OffererClosureForm(FlaskForm):
    comment = fields.PCCommentField("Motif de la fermeture (obligatoire)")
    zendesk_id = fields.PCOptIntegerField(
        "N° de ticket Zendesk",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )
    drive_link = fields.PCOptStringField(
        "Document Drive",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.URL(allow_ip=False, message="Le document doit être une URL"),
        ],
    )


class CommentAndTagOffererForm(OptionalCommentForm):
    tags = fields.PCQuerySelectMultipleField(
        "Tags Homologation",
        query_factory=_get_validation_tags_query,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: tag.label or tag.name,
    )


class BatchCommentAndTagOffererForm(empty_forms.BatchForm, CommentAndTagOffererForm):
    pass


class InviteUserForm(FlaskForm):
    email = fields.PCEmailField("Adresse email")


class OffererTagBaseForm(FlaskForm):
    name = fields.PCStringField(
        "Nom",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=140, message="Doit contenir moins de %(max)d caractères"),
            wtforms.validators.Regexp(TAG_NAME_REGEX, message="Le nom ne doit contenir aucun caractère d'espacement"),
        ),
    )
    label = fields.PCOptStringField(
        "Libellé", validators=(wtforms.validators.Length(max=140, message="Doit contenir moins de %(max)d caractères"),)
    )


class EditOffererTagForm(OffererTagBaseForm):
    description = fields.PCOptStringField(
        "Description",
        validators=(wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),),
    )
    # choices added later so as to query the categories only once
    categories = fields.PCSelectMultipleField("Catégories", coerce=int)


class CreateOffererTagCategoryForm(OffererTagBaseForm):
    pass


class IndividualOffererSubscriptionForm(FlaskForm):
    # full_opacity=True ensures that read-only view does not look disabled
    is_criminal_record_received = fields.PCSwitchBooleanField(
        "Casier judiciaire reçu", full_row=True, full_opacity=True
    )
    date_criminal_record_received = fields.PCOptDateField("Date de réception")
    is_certificate_received = fields.PCSwitchBooleanField("Diplôme reçu", full_row=True, full_opacity=True)
    certificate_details = fields.PCTextareaField("Type de diplôme / niveau")
    is_experience_received = fields.PCSwitchBooleanField("Expérience reçue", full_row=True, full_opacity=True)
    experience_details = fields.PCTextareaField("Type d'expérience")
    has_1yr_experience = fields.PCSwitchBooleanField("1 à 4 ans", full_opacity=True)
    has_4yr_experience = fields.PCSwitchBooleanField("+ 5 ans", full_opacity=True)
    is_certificate_valid = fields.PCSwitchBooleanField("Validité du diplôme", full_row=True, full_opacity=True)

    def __init__(self, *args: typing.Any, read_only: bool = False, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        if read_only:
            self.is_criminal_record_received.flags.readonly = True
            self.date_criminal_record_received.flags.readonly = True
            self.is_certificate_received.flags.readonly = True
            self.certificate_details.flags.readonly = True
            self.is_experience_received.flags.readonly = True
            self.experience_details.flags.readonly = True
            self.has_1yr_experience.flags.readonly = True
            self.has_4yr_experience.flags.readonly = True
            self.is_certificate_valid.flags.readonly = True
