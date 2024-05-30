import re
import typing

from flask_wtf import FlaskForm
import sqlalchemy as sa
import wtforms

from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.offerers import models as offerers_models
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.utils import get_regions_choices


TAG_NAME_REGEX = r"^[^\s]+$"
DIGITS_AND_WHITESPACES_REGEX = re.compile(r"^[\d\s]+$")


def _get_all_tags_query() -> sa.orm.Query:
    return offerers_models.OffererTag.query.order_by(offerers_models.OffererTag.label).options(
        sa.orm.load_only(
            offerers_models.OffererTag.id, offerers_models.OffererTag.name, offerers_models.OffererTag.label
        )
    )


def _get_validation_tags_query() -> sa.orm.Query:
    return (
        offerers_models.OffererTag.query.join(offerers_models.OffererTagCategoryMapping)
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
        "Nom de la structure",
        validators=(
            wtforms.validators.DataRequired("Le nom est obligatoire"),
            wtforms.validators.Length(max=140, message="doit contenir moins de %(max)d caractères"),
        ),
    )
    postal_address_autocomplete = fields.PcPostalAddressAutocomplete(
        "Adresse",
        street="street",
        city="city",
        ban_id="ban_id",
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
    city = fields.PCHiddenField(
        "Ville",
        validators=(
            wtforms.validators.Length(min=1, max=50, message="doit contenir entre %(min)d et %(max)d caractères"),
        ),
    )
    postal_code = fields.PCPostalCodeHiddenField("Code postal")


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

    q = fields.PCOptSearchField(
        "Nom de structure, SIREN, code postal, dép., ville, email, nom de compte pro, ID DMS CB"
    )
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
        "Auteur de la dernière action",
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
    per_page = fields.PCSelectField(
        "Par page",
        choices=(("10", "10"), ("25", "25"), ("50", "50"), ("100", "100")),
        default="100",
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
            if q.data.isnumeric() and len(q.data) not in (2, 3, 5, 9, 12):
                raise wtforms.validators.ValidationError(
                    "Le nombre de chiffres ne correspond pas à un SIREN, code postal, département ou ID DMS CB"
                )
        return q


class UserOffererValidationListForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Nom de structure, SIREN, code postal, département, ville, email, nom de compte pro")
    regions = fields.PCSelectMultipleField("Régions", choices=get_regions_choices())
    tags = fields.PCQuerySelectMultipleField(
        "Tags",
        query_factory=_get_validation_tags_query,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: tag.label or tag.name,
    )
    status = fields.PCSelectMultipleField(
        "États de la demande de rattachement",
        choices=utils.choices_from_enum(ValidationStatus, filters.format_validation_status),
    )
    instructors = fields.PCTomSelectField(
        "Auteur de la dernière action",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_bo_users",
    )
    offerer_status = fields.PCSelectMultipleField(
        "États de la structure", choices=utils.choices_from_enum(ValidationStatus, filters.format_validation_status)
    )
    from_date = fields.PCDateField("Demande à partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Demande jusqu'au", validators=(wtforms.validators.Optional(),))

    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    per_page = fields.PCSelectField(
        "Par page",
        choices=(("10", "10"), ("25", "25"), ("50", "50"), ("100", "100")),
        default="100",
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
            if q.data.isnumeric() and len(q.data) not in (2, 3, 5, 9):
                raise wtforms.validators.ValidationError(
                    "Le nombre de chiffres ne correspond pas à un SIREN, code postal ou département"
                )
        return q


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour la structure")


class OptionalCommentForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne")


class BatchOptionalCommentForm(empty_forms.BatchForm, OptionalCommentForm):
    pass


class CommentAndTagOffererForm(OptionalCommentForm):
    tags = fields.PCQuerySelectMultipleField(
        "Tags Homologation",
        query_factory=_get_validation_tags_query,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: tag.label or tag.name,
    )


class BatchCommentAndTagOffererForm(empty_forms.BatchForm, CommentAndTagOffererForm):
    pass


class TopActorForm(FlaskForm):
    # Optional because the request is sent with an empty value when disabled, "on" when enabled
    is_top_actor = wtforms.HiddenField("Top acteur", validators=(wtforms.validators.Optional(),))


class AddProUserForm(FlaskForm):
    pro_user_id = fields.PCSelectField("Compte pro", choices=[], validate_choice=False, coerce=int)
    comment = fields.PCCommentField("Commentaire interne")

    # Empty choice is proposed to avoid select first user by default, but empty choice is not allowed
    def validate_pro_user_id(self, pro_user_id: fields.PCSelectField) -> fields.PCSelectField:
        if not pro_user_id.data:
            raise wtforms.validators.ValidationError("Aucun compte pro n'est sélectionné")
        return pro_user_id


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
    is_email_sent = fields.PCSwitchBooleanField("Mail envoyé à l'acteur", full_row=True, full_opacity=True)
    date_email_sent = fields.PCOptDateField("Date d'envoi")
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
            self.is_email_sent.flags.readonly = True
            self.date_email_sent.flags.readonly = True
            self.is_criminal_record_received.flags.readonly = True
            self.date_criminal_record_received.flags.readonly = True
            self.is_certificate_received.flags.readonly = True
            self.certificate_details.flags.readonly = True
            self.is_experience_received.flags.readonly = True
            self.experience_details.flags.readonly = True
            self.has_1yr_experience.flags.readonly = True
            self.has_4yr_experience.flags.readonly = True
            self.is_certificate_valid.flags.readonly = True
