import re

import wtforms
from flask import flash
from flask_wtf import FlaskForm

from pcapi.core.providers import repository as providers_repository

from ..forms import fields


class SearchPivotForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID ou nom de partenaire culturel, identifiant cinéma")


class EditPivotForm(FlaskForm):
    venue_id = fields.PCTomSelectField(
        "Partenaire culturel",
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
        coerce=int,
        validators=(wtforms.validators.DataRequired("Information obligatoire"),),
    )


class EditAllocineForm(EditPivotForm):
    theater_id = fields.PCStringField(
        "Identifiant cinéma (Allociné)",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=20, message="Doit contenir au maximum %(max)d caractères"),
        ),
    )
    internal_id = fields.PCStringField("Identifiant interne Allociné")


class EditBoostForm(EditPivotForm):
    cinema_id = fields.PCStringField("Identifiant Cinéma (Boost)")
    cinema_url = fields.PCStringField(
        "URL du cinéma (Boost)",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.URL("Doit avoir la forme d'une URL"),
        ),
    )

    def validate(self, extra_validators: dict | None = None) -> bool:
        # do not use this custom validation on DeleteForm
        if not isinstance(self, EditBoostForm):
            return super().validate(extra_validators)

        boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")
        pivot = providers_repository.get_pivot_for_id_at_provider(
            id_at_provider=self.cinema_id.data, provider_id=boost_provider.id
        )
        if pivot and pivot.venueId != self.venue_id.data[0]:
            flash("Cet identifiant cinéma existe déjà pour un autre partenaire culturel", "warning")
            return False

        return super().validate(extra_validators)


class EditCGRForm(EditPivotForm):
    cinema_id = fields.PCStringField("Identifiant Cinéma (CGR)")
    cinema_url = fields.PCStringField(
        "URL du cinéma (CGR)",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.URL("Doit avoir la forme d'une URL"),
        ),
    )
    password = fields.PCPasswordField("Mot de passe (CGR)")

    def validate(self, extra_validators: dict | None = None) -> bool:
        # do not use this custom validation on DeleteForm
        if not isinstance(self, EditCGRForm):
            return super().validate(extra_validators)

        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        pivot = providers_repository.get_pivot_for_id_at_provider(
            id_at_provider=self.cinema_id.data, provider_id=cgr_provider.id
        )
        if pivot and pivot.venueId != self.venue_id.data[0]:
            flash("Cet identifiant cinéma existe déjà pour un autre partenaire culturel", "warning")
            return False

        return super().validate(extra_validators)


class EditCineOfficeForm(EditPivotForm):
    cinema_id = fields.PCStringField("Identifiant cinéma (CDS)")
    account_id = fields.PCStringField("Nom de compte (CDS)")
    api_token = fields.PCStringField("Clé API (CDS)")

    def validate_account_id(self, account_id: fields.PCStringField) -> fields.PCStringField:
        # account_id is used to build a url; only some specific characters are allowed
        if not re.match("^[a-zA-Z0-9_-]+$", account_id.data):
            raise wtforms.validators.ValidationError(
                "Le nom de compte ne peut pas contenir de caractères autres que chiffres, lettres et tirets"
            )
        return account_id

    def validate(self, extra_validators: dict | None = None) -> bool:
        # do not use this custom validation on DeleteForm
        if not isinstance(self, EditCineOfficeForm):
            return super().validate(extra_validators)

        cds_provider = providers_repository.get_provider_by_local_class("CDSStocks")
        pivot = providers_repository.get_pivot_for_id_at_provider(
            id_at_provider=self.cinema_id.data, provider_id=cds_provider.id
        )
        if pivot and pivot.venueId != self.venue_id.data[0]:
            flash("Cet identifiant cinéma existe déjà pour un autre partenaire culturel", "warning")
            return False

        return super().validate(extra_validators)


class EditEMSForm(EditPivotForm):
    cinema_id = fields.PCStringField("Identifiant cinéma (EMS)")
    last_version = fields.PCDateField(
        "Dernière synchronisation réussie (optionnel)", validators=[wtforms.validators.Optional()]
    )

    def validate(self, extra_validators: dict | None = None) -> bool:
        if not isinstance(self, EditEMSForm):
            return super().validate(extra_validators)

        ems_provider = providers_repository.get_provider_by_local_class("EMSStocks")
        if not ems_provider:
            flash("Le provider EMS n'existe pas.", "warning")
            return False

        pivot = providers_repository.get_pivot_for_id_at_provider(
            id_at_provider=self.cinema_id.data, provider_id=ems_provider.id
        )
        if pivot and pivot.venueId != self.venue_id.data[0]:
            flash("Cet identifiant cinéma existe déjà pour un autre partenaire culturel", "warning")
            return False

        return super().validate(extra_validators)
