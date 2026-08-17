import datetime
import enum
import json
import typing

import sqlalchemy.orm as sa_orm
import wtforms
from flask import flash
from flask import g
from flask_wtf import FlaskForm
from wtforms import validators

from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance import models as finance_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import search as search_forms
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.utils import advanced_search
from pcapi.routes.backoffice.utils import geography as geography_utils
from pcapi.utils import countries as countries_utils
from pcapi.utils import string as string_utils


class AdvancedFormFieldKeys(enum.Enum):
    BIRTHDAY = "Date de naissance"
    CREDIT = "Crédit"
    DEPOSIT_EXPIRATION_DATE = "Date d’expiration du crédit"
    EMAIL_DOMAIN = "Nom de domaine de l'email"
    IS_SUSPENDED = "Compte suspendu"
    REGION = "Région"
    TAG = "Tag"


TAG_NAME_REGEX = r"^[^\s]+$"


ADVANCED_FORM_FIELDS_CONFIG: dict[str, dict[str, typing.Any]] = {
    AdvancedFormFieldKeys.BIRTHDAY.name: {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    AdvancedFormFieldKeys.CREDIT.name: {"field": "credit", "operator": ["IN", "NOT_IN"]},
    AdvancedFormFieldKeys.DEPOSIT_EXPIRATION_DATE.name: {
        "field": "date",
        "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"],
    },
    AdvancedFormFieldKeys.EMAIL_DOMAIN.name: {
        "field": "string",
        "operator": ["EQUALS", "NOT_EQUALS"],
    },
    AdvancedFormFieldKeys.IS_SUSPENDED.name: {"field": "boolean", "operator": ["NULLABLE"]},
    AdvancedFormFieldKeys.REGION.name: {"field": "region", "operator": ["IN", "NOT_IN"]},
    AdvancedFormFieldKeys.TAG.name: {"field": "tag", "operator": ["IN", "NOT_IN"]},
}


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


def _get_tags() -> list[users_models.UserTag]:
    # cached per request: shared between TagAccountForm and the advanced search tags filter
    if not hasattr(g, "_account_tags"):
        g._account_tags = _get_tags_query().all()
    return g._account_tags


def _get_tags_choices() -> list[tuple[int, str]]:
    return [(tag.id, str(tag)) for tag in _get_tags()]


class GetAccountDetailsSearchForm(utils.PCForm):
    class Meta:
        csrf = False
        locales = ["fr_FR", "fr"]

    method = "GET"

    q = fields.PCOptStringField(
        label="Recherche (prénom et nom, ID ou liste d'IDs, email ou liste d'emails, téléphone)",
        validators=[validators.Optional(strip_whitespace=True)],
        full_width=True,
    )

    def is_empty(self) -> bool:
        return not self.q.data


class AccountsSearchSubForm(utils.PCForm):
    class Meta:
        csrf = False
        locales = ["fr_FR", "fr"]

    json_data = json.dumps(
        {
            "display_configuration": ADVANCED_FORM_FIELDS_CONFIG,
            "all_available_fields": [
                "boolean",
                "credit",
                "date",
                "region",
                "string",
                "tag",
            ],
            "sub_rule_type_field_name": "search_field",
            "operator_field_name": "operator",
        }
    )

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=utils.choices_from_enum(AdvancedFormFieldKeys, sort=True),
        validators=[
            wtforms.validators.Optional(strip_whitespace=True),
        ],
    )
    operator = fields.PCSelectField(
        "Opérateur",
        choices=utils.choices_from_enum(advanced_search.AdvancedSearchOperators),
        default=advanced_search.AdvancedSearchOperators.EQUALS,
        validators=[
            wtforms.validators.Optional(strip_whitespace=True),
        ],
    )
    boolean = fields.PCSelectField(
        "Booléen",
        choices=(("true", "Oui"), ("false", "Non")),
        default="true",
        validators=[
            wtforms.validators.Optional(strip_whitespace=True),
        ],
    )
    credit = fields.PCSelectMultipleField(
        "Crédit",
        choices=utils.choices_from_enum(
            search_forms.AccountSearchFilter, exclude_opts=(search_forms.AccountSearchFilter.SUSPENDED,)
        ),
        field_list_compatibility=True,
        search_inline=True,
    )
    date = fields.PCOptDateField()
    region = fields.PCSelectMultipleField(
        "Région",
        choices=geography_utils.get_regions_choices(),
        field_list_compatibility=True,
        search_inline=True,
    )
    string = fields.PCOptStringField(
        "Texte",
        validators=[
            wtforms.validators.Length(max=4096, message="Doit contenir moins de %(max)d caractères"),
        ],
    )
    tag = fields.PCSelectMultipleField(
        "Tag",
        coerce=int,
        field_list_compatibility=True,
        search_inline=True,
    )

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)
        self.tag.choices = _get_tags_choices()


class GetAccountsListSearchForm(utils.PCForm):
    class Meta:
        csrf = False
        locales = ["fr_FR", "fr"]

    method = "GET"

    form_field_configuration = ADVANCED_FORM_FIELDS_CONFIG
    search_attributes = AdvancedFormFieldKeys

    q = fields.PCOptStringField(
        label="Recherche (prénom et nom, ID ou liste d'IDs, email ou liste d'emails, téléphone)",
        full_width=True,
        validators=[validators.Optional(strip_whitespace=True)],
    )
    search = fields.PCFieldListField(
        fields.PCFormField(AccountsSearchSubForm),
        label="recherches",
        min_entries=1,
    )

    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (100, "Afficher 100 résultats maximum"),
            (1000, "Afficher 1000 résultats maximum"),
        ),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def is_empty(self) -> bool:
        if self.q.data:
            return False

        for search_field_data in self.search.data:
            if not self._is_search_field_data_empty(search_field_data):
                return False

        return True

    def validate(self, extra_validators: dict | None = None) -> bool:
        errors = []

        query_str = self.q.data.strip(" \t,;") if self.q.data else ""
        if "%" in query_str:
            errors.append("Le caractère % n'est pas autorisé")
        elif (
            query_str
            and len(query_str) < 3
            and not string_utils.is_numeric(query_str)
            and all(self._is_search_field_data_empty(search_field_data) for search_field_data in self.search.data)
        ):
            errors.append("Attention, la recherche doit contenir au moins 3 lettres.")

        for search_field_data in self.search.data:
            if search_field := search_field_data.get("search_field"):
                if self._is_search_field_data_empty(search_field_data):
                    try:
                        errors.append(f"Le filtre « {self.search_attributes[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")
                else:
                    operator = search_field_data.get("operator")
                    if operator not in self.form_field_configuration.get(search_field, {}).get("operator", []):
                        try:
                            errors.append(
                                f"L'opérateur « {advanced_search.AdvancedSearchOperators[operator].value} » n'est pas supporté par le filtre {self.search_attributes[search_field].value}."
                            )
                        except KeyError:
                            errors.append(f"L'opérateur {operator} n'est pas supporté par le filtre {search_field}.")

        if errors:
            flash("\n".join(errors), "warning")
            return False

        query_terms = query_str.split()
        if len(query_terms) > 1 and all(len(term) <= 3 for term in query_terms):
            flash("Les termes étant très courts, la recherche n'a porté que sur le nom complet exact.", "info")

        return super().validate(extra_validators)

    def _is_search_field_data_empty(self, search_field_data: dict[str, typing.Any]) -> bool:
        field_name = search_field_data.get("search_field")
        if field_name:
            field_attribute_name = self.form_field_configuration.get(field_name, {}).get("field", "")
            field_data = search_field_data.get(field_attribute_name)
            if field_data not in (None, []):
                return False

        return True


class EditAccountForm(utils.PCForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
    birth_date = fields.PCOptDateField("Date de naissance")
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


class QFBonusCreditRequestForm(FlaskForm):
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


class DisabilityBonusCreditRequestForm(FlaskForm):
    birth_country = fields.PCSelectWithPlaceholderValueField(
        "Pays de naissance du jeune",
        choices=countries_utils.INSEE_COUNTRIES,
    )
    birth_city = fields.PCTomSelectField(
        "Ville de naissance du jeune (s'il est né en France)",
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
                self.birth_city.errors = ["obligatoire lorsque le jeune est né en France"]
                return False
        elif city_data:
            self.birth_city.errors = ["doit rester vide lorsque le jeune n'est pas né en France"]
            return False
        return super().validate(extra_validators)


class ExtendCreditForm(FlaskForm):
    expiration_date = fields.PCDateField(
        "Nouvelle date d'expiration du crédit",
        validators=[
            validators.DataRequired("Information obligatoire"),
            fields.DateRangeValidator(
                message=f"Le crédit peut être prolongé jusqu'à {users_constants.MAX_DEPOSIT_EXTENSION_DAYS} jours à compter d'aujourd'hui.",
                min=datetime.date.today(),
                max=datetime.date.today() + datetime.timedelta(days=users_constants.MAX_DEPOSIT_EXTENSION_DAYS),
            ),
        ],
    )

    def __init__(self, deposit: finance_models.Deposit, **kwargs: typing.Any):
        super().__init__(**kwargs)
        assert deposit.expirationDate is not None  # helps mypy
        self._current_expiration_date = deposit.expirationDate

    def validate_expiration_date(self, field: fields.PCDateField) -> fields.PCDateField:
        if field.data <= self._current_expiration_date.date():
            raise wtforms.ValidationError("La nouvelle date doit être postérieure à la date d'expiration actuelle.")

        return field


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
        query_factory=_get_tags,
        get_pk=lambda tag: tag.id,
        get_label=lambda tag: str(tag),
    )


class TagFraudulentBookingsForm(utils.PCForm):
    send_mails = fields.PCSwitchBooleanField("Envoyer un mail d'avertissement aux acteurs culturels", full_row=True)


class GetIdDocumentForm(utils.PCForm):
    username = fields.PCStringField("Identifiant de clé d'accès")
    password = fields.PCPasswordField("Clé d'accès secrète")


class DisconnectNativeUserForm(utils.PCForm):
    comment = fields.PCOptCommentField("Commentaire facultatif à propos de la déconnexion")
