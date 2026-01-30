import datetime
import enum

import sqlalchemy.orm as sa_orm
import wtforms
from flask import flash
from flask_wtf import FlaskForm

from pcapi.connectors.dms import models as dms_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import search
from pcapi.routes.backoffice.forms import utils
from pcapi.utils import countries as countries_utils
from pcapi.utils import string as string_utils


TAG_NAME_REGEX = r"^[^\s]+$"


def _get_tags_query() -> sa_orm.Query:
    return (
        db.session.query(users_models.UserTag)
        .order_by(users_models.UserTag.label)
        .options(
            sa_orm.load_only(
                users_models.UserTag.id,
                users_models.UserTag.name,
                users_models.UserTag.label,
            )
        )
    )


class AccountSearchForm(search.SearchForm):
    q = fields.PCOptSearchField(label="")
    filter = fields.PCSelectMultipleField("Crédits", choices=utils.choices_from_enum(search.AccountSearchFilter))
    # choices added later so as to query the tags only once
    tag = fields.PCSelectMultipleField("Tags", coerce=int)

    def validate(self) -> bool:
        if not super().validate():
            return False
        query_str = self.q.data.strip(" \t,;") if self.q.data else ""
        if not self.tag.data and not self.filter.data and len(query_str) < 3 and not string_utils.is_numeric(query_str):
            self.q.errors += ("Attention, la recherche doit contenir au moins 3 lettres.",)
            return False
        split_data = query_str.split()
        if len(split_data) > 1 and all(len(item) <= 3 for item in split_data):
            flash("Les termes étant très courts, la recherche n'a porté que sur le nom complet exact.", "info")
        return True


class EditAccountForm(utils.PCForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
    birth_date = fields.PCDateField("Date de naissance")
    phone_number = fields.PCOptStringField("Numéro de téléphone")
    id_piece_number = fields.PCOptStringField("N° pièce d'identité")
    postal_address_autocomplete = fields.PcPostalAddressAutocomplete(
        "Adresse",
        street="street",
        ban_id="ban_id",
        insee_code="insee_code",
        city="city",
        postal_code="postal_code",
        latitude=None,
        longitude=None,
        required=False,
        has_reset=True,
        has_manual_editing=True,
        limit=10,
    )
    street = fields.PCOptStringField("Adresse", initially_hidden=True)
    postal_code = fields.PCOptPostalCodeField("Code postal", initially_hidden=True)
    city = fields.PCOptStringField("Ville", initially_hidden=True)
    marketing_email_subscription = fields.PCSwitchBooleanField("Abonné aux emails marketing", full_row=True)


class ManualReviewForm(FlaskForm):
    status = fields.PCSelectWithPlaceholderValueField(
        "Statut",
        choices=utils.choices_from_enum(
            subscription_models.FraudReviewStatus, formatter=filters.format_fraud_review_status
        ),
    )
    eligibility = fields.PCSelectWithPlaceholderValueField(
        "Éligibilité",
        choices=utils.choices_from_enum(users_models.EligibilityType, formatter=filters.format_eligibility_type),
    )
    reason = fields.PCOptCommentField("Raison du changement")


class BonusCreditRequestForm(FlaskForm):
    civility = fields.PCSelectWithPlaceholderValueField(
        "Civilité du représentant légal",
        choices=utils.choices_from_enum(users_models.GenderEnum, formatter=filters.format_gender, sort=True),
    )
    first_names = fields.PCStringField("Prénoms du représentant légal")
    last_name = fields.PCStringField("Nom de naissance du représentant légal")
    common_name = fields.PCOptStringField("Nom d'usage du représentant légal")
    birth_date = fields.PCDateField("Date de naissance du représentant légal")
    birth_country = fields.PCSelectWithPlaceholderValueField(
        "Pays de naissance du représentant légal", choices=countries_utils.INSEE_COUNTRIES
    )
    birth_city = fields.PCTomSelectField(
        "Ville de naissance du représentant légal (s'il est né en France)",
        multiple=False,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_cities",
    )

    def validate(self, extra_validators: dict | None = None) -> bool:
        country_data = self.birth_country.data
        city_data = self.birth_city.single_data
        if country_data == countries_utils.FRANCE_INSEE_CODE:
            if not city_data:
                self.birth_city.errors = ["obligatoire lorsque le représentant légal est né en France"]
                return False
        elif city_data:
            self.birth_city.errors = ["doit rester vide lorsque le représentant légal n'est pas né en France"]
            return False
        return super().validate(extra_validators)


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte jeune")


class AccountUpdateRequestSearchForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Numéro de dossier")
    from_to_date = fields.PCDateRangeField(
        "Modifiés entre",
        validators=(wtforms.validators.Optional(),),
        max_date=datetime.date.today(),
        reset_to_blank=True,
    )
    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    order = wtforms.HiddenField(
        "order", default="desc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )
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
    has_found_user = fields.PCSelectMultipleField(
        "Compte jeune",
        choices=(("true", "Avec compte jeune"), ("false", "Sans compte jeune")),
    )
    status = fields.PCSelectMultipleField(
        "État",
        choices=utils.choices_from_enum(
            dms_models.GraphQLApplicationStates, formatter=filters.format_dms_application_status
        ),
    )
    update_type = fields.PCSelectMultipleField(
        "Type de demande",
        choices=utils.choices_from_enum(
            users_models.UserAccountUpdateType, formatter=filters.format_user_account_update_type
        ),
    )
    flags = fields.PCSelectMultipleField(
        "Marqueur",
        choices=utils.choices_from_enum(
            users_models.UserAccountUpdateFlag, formatter=filters.format_user_account_update_flag
        ),
    )

    last_instructor = fields.PCTomSelectField(
        "Dernier instructeur",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_bo_users",
    )

    only_unassigned = fields.PCSwitchBooleanField(
        "Uniquement les dossiers non affectés",
        full_row=True,
    )


class AccountUpdateRequestAcceptForm(utils.PCForm):
    motivation = fields.PCOptCommentField("Explication facultative envoyée au demandeur sur Démarche Numérique")


class CorrectionReasonOptions(enum.Enum):
    REFUSED_FILE = "refused-file"
    UNREADABLE_PHOTO = "unreadable-photo"
    MISSING_FILE = "missing-file"


class AccountUpdateRequestCorrectionForm(utils.PCForm):
    correction_reason = fields.PCSelectField(
        "Raison de demande de correction",
        choices=utils.values_from_enum(CorrectionReasonOptions),
    )


class AccountUpdateRequestSelectUserForm(utils.PCForm):
    user = fields.PCTomSelectField(
        "Compte jeune",
        choices=[],
        validate_choice=True,
        endpoint="backoffice_web.autocomplete_public_users",
    )

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)
        autocomplete.prefill_public_users_choices(self.user)


class UserTagBaseForm(FlaskForm):
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


class EditUserTagForm(UserTagBaseForm):
    description = fields.PCOptStringField(
        "Description",
        validators=(wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),),
    )
    # choices added later so as to query the categories only once
    categories = fields.PCSelectMultipleField("Catégories", coerce=int)


class CreateUserTagCategoryForm(UserTagBaseForm):
    pass


class TagAccountForm(FlaskForm):
    tags = fields.PCQuerySelectMultipleField(
        "Tags",
        query_factory=_get_tags_query,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: str(tag),
    )


class TagFraudulentBookingsForm(utils.PCForm):
    send_mails = fields.PCSwitchBooleanField("Envoyer un mail d'avertissement aux acteurs culturels", full_row=True)
