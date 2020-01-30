import re
from typing import List

import sqlalchemy
from schwifty import BIC, IBAN
from sqlalchemy import CHAR, Column, Float, Integer, String
from sqlalchemy.exc import DataError, IntegrityError, InternalError

from models import (ApiErrors, BankInformation, HasAddressMixin, Offer, Offerer,
                    PcObject, Product, Stock, User, Venue)
from models.db import Model, db
from repository import offerer_queries, user_queries, venue_queries


def delete(*models: List[Model]) -> None:
    for model in models:
        db.session.delete(model)
    db.session.commit()


def errors(model: Model) -> ApiErrors:
    api_errors = _generic_errors(model)

    if api_errors.errors:
        return api_errors

    if isinstance(model, HasAddressMixin):
        api_errors = _get_has_address_mixin_errors(model, api_errors)

    if isinstance(model, BankInformation):
        api_errors = _get_bank_information_errors(model, api_errors)
    elif isinstance(model, Offer):
        api_errors = _get_offer_errors(model, api_errors)
    elif isinstance(model, Offerer):
        api_errors = _get_offerer_errors(model, api_errors)
    elif isinstance(model, Product):
        api_errors = _get_product_errors(model, api_errors)
    elif isinstance(model, Stock):
        api_errors = _get_stock_errors(model, api_errors)
    elif isinstance(model, User):
        api_errors = _get_user_errors(model, api_errors)
    elif isinstance(model, Venue):
        api_errors = _get_venue_errors(model, api_errors)

    return api_errors


def save(*models: List[Model]) -> None:
    if not models:
        return None

    api_errors = ApiErrors()
    for model in models:
        with db.session.no_autoflush:
            model_api_errors = errors(model)
        if model_api_errors.errors.keys():
            api_errors.errors.update(model_api_errors.errors)
        else:
            db.session.add(model)

    if api_errors.errors.keys():
        raise api_errors

    try:
        db.session.commit()
    except DataError as data_error:
        api_errors.add_error(*model.restize_data_error(data_error))
        db.session.rollback()
        raise api_errors
    except IntegrityError as integrity_error:
        api_errors.add_error(*model.restize_integrity_error(integrity_error))
        db.session.rollback()
        raise api_errors
    except InternalError as internal_error:
        api_errors.add_error(*model.restize_internal_error(internal_error))
        db.session.rollback()
        raise api_errors
    except TypeError as type_error:
        api_errors.add_error(*PcObject.restize_type_error(type_error))
        db.session.rollback()
        raise api_errors
    except ValueError as value_error:
        api_errors.add_error(*PcObject.restize_value_error(value_error))
        db.session.rollback()
        raise api_errors

    if api_errors.errors.keys():
        raise api_errors


def _generic_errors(model: Model) -> ApiErrors:
    api_errors = ApiErrors()
    columns = model.__class__.__table__.columns._data

    for key in columns.keys():
        column = columns[key]
        value = getattr(model, key)

        if not isinstance(column, Column):
            continue

        if not column.nullable \
                and not column.foreign_keys \
                and not column.primary_key \
                and column.default is None \
                and value is None:
            api_errors.add_error(key, 'Cette information est obligatoire')

        if value is None:
            continue

        if (isinstance(column.type, String) or isinstance(column.type, CHAR)) \
                and not isinstance(column.type, sqlalchemy.Enum) \
                and not isinstance(value, str):
            api_errors.add_error(key, 'doit être une chaîne de caractères')

        if (isinstance(column.type, String) or isinstance(column.type, CHAR)) \
                and isinstance(value, str) \
                and column.type.length \
                and len(value) > column.type.length:
            api_errors.add_error(key, f'Vous devez saisir moins de {str(column.type.length)} caractères')

        if isinstance(column.type, Integer) \
                and not isinstance(value, int):
            api_errors.add_error(key, 'doit être un entier')

        if isinstance(column.type, Float) \
                and not isinstance(value, float):
            api_errors.add_error(key, 'doit être un nombre')

    return api_errors


def _get_bank_information_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    try:
        IBAN(model.iban)
    except (ValueError, TypeError):
        api_errors.add_error('iban', f"L'IBAN renseigné (\"{model.iban}\") est invalide")

    try:
        BIC(model.bic)
    except (ValueError, TypeError):
        api_errors.add_error('bic', f'Le BIC renseigné ("{model.bic}") est invalide')

    return api_errors


def _get_has_address_mixin_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.postalCode is not None and not re.match(r'^\d[AB0-9]\d{3,4}$', model.postalCode):
        api_errors.add_error('postalCode', 'Ce code postal est invalide')

    return api_errors


def _get_offer_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    venue = model.venue if model.venue else venue_queries.find_by_id(model.venueId)

    if model.isDigital:
        if not venue.isVirtual:
            api_errors.add_error('venue', 'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"')
        if model.type_can_only_be_offline():
            api_errors.add_error('url', f'Une offre de type {model.get_label_from_type_string()} ne peut pas être numérique')
    else:
        if venue.isVirtual:
            api_errors.add_error('venue', 'Une offre physique ne peut être associée au lieu "Offre numérique"')

    return api_errors


def _get_offerer_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.siren is not None and (not len(model.siren) == 9):
        api_errors.add_error('siren', 'Ce code SIREN est invalide')

    return api_errors


def _get_product_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.isDigital and model.type_can_only_be_offline():
        api_errors.add_error('url', f'Une offre de type {model.get_label_from_type_string()} ne peut pas être numérique')

    return api_errors


def _get_stock_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.available is not None and model.available < 0:
        api_errors.add_error('available', 'Le stock doit être positif')

    if model.endDatetime \
            and model.beginningDatetime \
            and model.endDatetime <= model.beginningDatetime:
        api_errors.add_error('endDatetime', "La date de fin de l'événement doit être postérieure à la date de début")

    return api_errors


def _get_user_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    user_count = 0
    try:
        user_count = user_queries.count_users_by_email(model.email)
    except IntegrityError:
        if model.id is None:
            api_errors.add_error('email', 'Un compte lié à cet e-mail existe déjà')

    if model.id is None and user_count > 0:
        api_errors.add_error('email', 'Un compte lié à cet e-mail existe déjà')
    if model.publicName:
        api_errors.check_min_length('publicName', model.publicName, 3)
    if model.email:
        api_errors.check_email('email', model.email)
    if model.isAdmin and model.canBookFreeOffers:
        api_errors.add_error('canBookFreeOffers', 'Admin ne peut pas réserver')
    if model.clearTextPassword:
        api_errors.check_min_length('password', model.clearTextPassword, 8)

    return api_errors


def _get_venue_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.siret is not None and not len(model.siret) == 14:
        api_errors.add_error('siret', f'Ce code SIRET est invalide : {model.siret}')
    if model.postalCode is not None and len(model.postalCode) != 5:
        api_errors.add_error('postalCode', 'Ce code postal est invalide')
    if model.managingOffererId is not None:
        if model.managingOfferer is None:
            managing_offerer = offerer_queries.find_by_id(model.managingOffererId)
        else:
            managing_offerer = model.managingOfferer

        if managing_offerer.siren is None:
            api_errors.add_error('siren', "Ce lieu ne peut enregistrer de SIRET car la structure associée n'a pas de SIREN renseigné")

        if model.siret is not None \
                and managing_offerer is not None \
                and not model.siret.startswith(managing_offerer.siren):
            api_errors.add_error('siret', 'Le code SIRET doit correspondre à un établissement de votre structure')

    return api_errors
