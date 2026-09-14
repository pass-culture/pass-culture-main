"""
Static catalogs and form states displayed on the backoffice design system page (dev/components).
"""

import datetime
import types
import typing

from . import forms


THEME_COLORS = ("primary", "secondary", "success", "info", "warning", "danger", "light", "dark")

SPACERS = (
    ("0", "0"),
    ("1", "0.25rem"),
    ("2", "0.5rem"),
    ("3", "1rem"),
    ("4", "1.5rem"),
    ("5", "3rem"),
    ("12", "0.75rem"),
    ("32", "2rem"),
    ("40", "2.5rem"),
    ("56", "3.5rem"),
)

FONT_WEIGHTS = (("fw-light", "Léger"), ("fw-normal", "Normal"), ("fw-medium", "Moyen"), ("fw-bold", "Gras"))

ICONS = (
    ("pencil-square", "Éditer"),
    ("trash3-fill", "Supprimer"),
    ("plus-lg", "Ajouter"),
    ("search", "Rechercher"),
    ("filetype-csv", "Télécharger un CSV"),
    ("filetype-xlsx", "Télécharger un XLSX"),
    ("cloud-download-fill", "Télécharger"),
    ("eye", "Voir"),
    ("copy", "Copier"),
    ("box-arrow-up-right", "Lien externe"),
    ("three-dots-vertical", "Menu d'actions"),
    ("arrow-down-up", "Colonne triable"),
    ("arrow-clockwise", "Rafraîchir"),
    ("arrow-right", "Suivant"),
    ("chevron-down", "Déplier"),
    ("chevron-up", "Replier"),
    ("info-circle", "Information"),
    ("exclamation-triangle", "Avertissement"),
    ("exclamation-triangle-fill", "Alerte"),
    ("check-circle-fill", "Validé"),
    ("x-circle-fill", "Refusé"),
    ("hourglass-split", "En attente"),
    ("pause-circle", "Suspendu"),
    ("x-lg", "Fermer / Effacer"),
    ("stars", "IA / suggestion"),
    ("tag", "Tag"),
    ("briefcase", "Entité juridique"),
    ("geo-alt-fill", "Localisation"),
    ("envelope-plus-fill", "Email modifié"),
    ("file-image", "Image manquante"),
    ("person-vcard", "Identité"),
    ("phone", "Téléphone"),
)

FILLED_FORM_DATA: dict[str, typing.Any] = {
    "checkbox": True,
    "stringfield": "Jean Dupont",
    "postal_code": "75001",
    "text_area": "Un commentaire\nsur deux lignes",
    "interger": 42,
    "decimal": "12.50",
    "date_time": datetime.datetime(2026, 9, 11, 14, 30),
    "date": datetime.date(2026, 9, 11),
    "select": 1,
    "multiselect": [1, 2],
    "switch": True,
}

FIELD_ERROR_MESSAGE = "Information obligatoire"

SAMPLE_OFFER = types.SimpleNamespace(id=1)


def _iter_fields(form: forms.SimpleComponentsForm) -> typing.Iterator[typing.Any]:
    for field in form:
        if field.name != "csrf_token":
            yield field


def build_filled_form() -> forms.SimpleComponentsForm:
    form = forms.SimpleComponentsForm(data=FILLED_FORM_DATA)
    form.password.data = form.stringfield.data  # any value renders as dots; no literal, to keep secret scanners quiet
    form.date_range.data = [datetime.date(2026, 9, 1), datetime.date(2026, 9, 30)]
    form.tomselect.choices = [(1, "Le Grand Rex")]
    form.tomselect.data = ["1"]
    return form


def build_errored_form() -> forms.SimpleComponentsForm:
    form = forms.SimpleComponentsForm()
    for field in _iter_fields(form):
        field.errors = [FIELD_ERROR_MESSAGE]
    return form


def build_disabled_form() -> forms.SimpleComponentsForm:
    form = build_filled_form()
    for field in _iter_fields(form):
        field.flags.disabled = True
        field.flags.readonly = True
    form.tomselect.readonly = True
    return form


def build_form_states() -> list[tuple[str, forms.SimpleComponentsForm]]:
    return [
        ("Par défaut", forms.SimpleComponentsForm()),
        ("Renseigné", build_filled_form()),
        ("En erreur", build_errored_form()),
        ("Désactivé", build_disabled_form()),
    ]
