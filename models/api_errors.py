""" api errors """
# coding=utf-8
import json


class ApiErrors(Exception):
    def __init__(self, errors: dict = None):
        self.errors = errors if errors else {}

    def addError(self, field, error):

        # SPECIFIC ERRORS FROM MODELS
        # HAPPEN FIRST, SO NO NEED TO ADD AFTER
        # PSQL GENERIC ERRORS COMING FROM PC_OBJECT
        # CHECK_AND_SAVE STATIC METHOD
        if field not in self.errors:
            self.errors[field] = [error]

    def checkDate(self, field, value):
        if (isinstance(value, str) or isinstance(value, unicode)) and re.search(
                '^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$', value):
            return True
        else:
            self.addError(field, 'Format de date incorrect')

    def checkFloat(self, field, value):
        if isinstance(value, float) or \
                ((isinstance(value, str) or isinstance(value, unicode)) and re.search('^\d+(\.\d*|)$', value)):
            return True
        else:
            self.addError(field, 'La valeur doit etre un nombre (optionnellement à virgule).')

    def checkWithin(self, field, value, min, max):
        self.checkUnder(field, value, max)
        self.checkOver(field, value, min)

    def checkOver(self, field, value, min):
        if value > min:
            return True
        else:
            self.addError(field, 'La valeur doit être supérieure à ' + str(min))

    def checkUnder(self, field, value, max):
        if value < min:
            return True
        else:
            self.addError(field, 'La valeur doit être inférieure à ' + str(min))

    def checkMinLength(self, field, value, length):
        if len(value) < length:
            self.addError(field, 'Vous devez saisir au moins ' + str(length) + ' caractères.')

    def checkEmail(self, field, value):
        if not "@" in value:
            self.addError(field, 'L\'e-mail doit contenir un @.')

    def maybeRaise(self):
        if len(self.errors) > 0:
            raise self

    def __str__(self):
        if self.errors:
            return json.dumps(self.errors, indent=2)

    status_code = None


class ResourceGoneError(ApiErrors):
    pass


class ResourceNotFound(ApiErrors):
    pass


class ForbiddenError(ApiErrors):
    pass


class DecimalCastError(ApiErrors):
    pass


class DateTimeCastError(ApiErrors):
    pass
