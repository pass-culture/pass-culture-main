import re
from typing import List

import sqlalchemy
from schwifty import IBAN, BIC
from sqlalchemy import Column, String, CHAR, Integer, Float
from sqlalchemy.exc import DataError, IntegrityError, InternalError

from models import ApiErrors, PcObject, User, BankInformation, Product, Offer, Venue, Stock, Offerer, HasAddressMixin
from models.db import db, Model


def delete(model: Model):
    db.session.delete(model)
    db.session.commit()


def delete_all(models: List[Model]):
    for model in models:
        db.session.delete(model)
    db.session.commit()


def errors(model: Model):
    api_errors = _generic_errors(model)
    if api_errors.errors:
        return api_errors
    elif isinstance(model, User):
        user_count = 0
        try:
            user_count = User.query.filter_by(email=model.email).count()
        except IntegrityError as ie:
            if model.id is None:
                api_errors.add_error('email', 'Un compte lié à cet email existe déjà')

        if model.id is None and user_count > 0:
            api_errors.add_error('email', 'Un compte lié à cet email existe déjà')
        if model.publicName:
            api_errors.check_min_length('publicName', model.publicName, 3)
        if model.email:
            api_errors.check_email('email', model.email)

        if model.isAdmin and model.canBookFreeOffers:
            api_errors.add_error('canBookFreeOffers', 'Admin ne peut pas booker')
        if model.clearTextPassword:
            api_errors.check_min_length('password', model.clearTextPassword, 8)

    elif isinstance(model, BankInformation):
        try:
            IBAN(model.iban)
        except (ValueError, TypeError):
            api_errors.add_error('iban', f"L'IBAN renseigné (\"{model.iban}\") est invalide")

        try:
            BIC(model.bic)
        except (ValueError, TypeError):
            api_errors.add_error('bic', f"Le BIC renseigné (\"{model.bic}\") est invalide")

    elif isinstance(model, Product):
        if model.isDigital and model._type_can_only_be_offline():
            api_errors.add_error('url', 'Une offre de type {} ne peut pas être numérique'.format(
                model._get_label_from_type_string()))

    elif isinstance(model, Offer):
        if model.venue:
            venue = model.venue
        else:
            venue = Venue.query.get(model.venueId)
        if model.isDigital and not venue.isVirtual:
            api_errors.add_error('venue',
                                 'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"')
        elif not model.isDigital and venue.isVirtual:
            api_errors.add_error('venue', 'Une offre physique ne peut être associée au lieu "Offre numérique"')
        if model.isDigital and model._type_can_only_be_offline():
            api_errors.add_error('url', 'Une offre de type {} ne peut pas être numérique'.format(
                model._get_label_from_type_string()))

    elif isinstance(model, Stock):
        if model.available is not None and model.available < 0:
            api_errors.add_error('available', 'Le stock doit être positif')

        if model.endDatetime \
                and model.beginningDatetime \
                and model.endDatetime <= model.beginningDatetime:
            api_errors.add_error('endDatetime',
                                 'La date de fin de l\'événement doit être postérieure à la date de début')

    elif isinstance(model, HasAddressMixin):
        if model.postalCode is not None \
                and not re.match('^\d[AB0-9]\d{3,4}$', model.postalCode):
            api_errors.add_error('postalCode', 'Ce code postal est invalide')

    elif isinstance(model, Offerer):
        if model.siren is not None \
                and (not len(model.siren) == 9):
            api_errors.add_error('siren', 'Ce code SIREN est invalide')

    elif isinstance(model, Venue):
        if model.siret is not None \
                and not len(model.siret) == 14:
            api_errors.add_error('siret', 'Ce code SIRET est invalide : ' + model.siret)
        if model.postalCode is not None \
                and len(model.postalCode) != 5:
            api_errors.add_error('postalCode', 'Ce code postal est invalide')
        if model.managingOffererId is not None:
            if model.managingOfferer is None:
                managingOfferer = Offerer.query \
                    .filter_by(id=model.managingOffererId).first()
            else:
                managingOfferer = model.managingOfferer
            if managingOfferer.siren is None:
                api_errors.add_error('siren',
                                     'Ce lieu ne peut enregistrer de SIRET car la structure associée n\'a pas de'
                                     + 'SIREN renseigné')
            if model.siret is not None \
                    and managingOfferer is not None \
                    and not model.siret.startswith(managingOfferer.siren):
                api_errors.add_error('siret', 'Le code SIRET doit correspondre à un établissement de votre structure')

    return api_errors


def save(*objects):
    if not objects:
        return None

    api_errors = ApiErrors()
    for obj in objects:
        with db.session.no_autoflush:
            obj_api_errors = errors(obj)
        if obj_api_errors.errors.keys():
            api_errors.errors.update(obj_api_errors.errors)
        else:
            db.session.add(obj)

    if api_errors.errors.keys():
        raise api_errors

    try:
        db.session.commit()
    except DataError as de:
        api_errors.add_error(*obj.restize_data_error(de))
        db.session.rollback()
        raise api_errors
    except IntegrityError as ie:
        for obj in objects:
            api_errors.add_error(*obj.restize_integrity_error(ie))
        db.session.rollback()
        raise api_errors
    except InternalError as ie:
        for obj in objects:
            api_errors.add_error(*obj.restize_internal_error(ie))
        db.session.rollback()
        raise api_errors
    except TypeError as te:
        api_errors.add_error(*PcObject.restize_type_error(te))
        db.session.rollback()
        raise api_errors
    except ValueError as ve:
        api_errors.add_error(*PcObject.restize_value_error(ve))
        db.session.rollback()
        raise api_errors

    if api_errors.errors.keys():
        raise api_errors


def _generic_errors(model: Model):
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
            api_errors.add_error(key,
                                 'Vous devez saisir moins de '
                                 + str(column.type.length)
                                 + ' caractères')
        if isinstance(column.type, Integer) \
                and not isinstance(value, int):
            api_errors.add_error(key, 'doit être un entier')
        if isinstance(column.type, Float) \
                and not isinstance(value, float):
            api_errors.add_error(key, 'doit être un nombre')
    return api_errors
