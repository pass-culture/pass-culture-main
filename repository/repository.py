from typing import List

import sqlalchemy
from schwifty import IBAN, BIC
from sqlalchemy import Column, String, CHAR, Integer, Float
from sqlalchemy.exc import DataError, IntegrityError, InternalError

from models import ApiErrors, PcObject, User, BankInformation
from models.db import db, Model


class Repository:
    def errors(self, model: Model):
        api_errors = self._generic_errors()
        if isinstance(model, User):
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

        if isinstance(model, BankInformation):
            try:
                IBAN(model.iban)
            except (ValueError, TypeError):
                api_errors.add_error('iban', f"L'IBAN renseigné (\"{model.iban}\") est invalide")

            try:
                BIC(model.bic)
            except (ValueError, TypeError):
                api_errors.add_error('bic', f"Le BIC renseigné (\"{model.bic}\") est invalide")

        return api_errors

    def _generic_errors(self):
        api_errors = ApiErrors()
        columns = self.__class__.__table__.columns._data
        for key in columns.keys():
            column = columns[key]
            value = getattr(self, key)
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

    @staticmethod
    def save(*objects):
        if not objects:
            return None

        api_errors = ApiErrors()
        for obj in objects:
            with db.session.no_autoflush:
                obj_api_errors = obj.errors()
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

    @staticmethod
    def delete(model: Model):
        db.session.delete(model)
        db.session.commit()

    @staticmethod
    def delete_all(models: List[Model]):
        for model in models:
            db.session.delete(model)
        db.session.commit()
