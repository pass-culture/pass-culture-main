# coding=utf-8
from flask import current_app as app

class ApiErrors(Exception):
    def __init__(self):
        self.errors = []

    def addError(self, **kargs):
        self.errors.append({'field': kargs['field'], 'errtype': kargs['errtype'], 'error': kargs['error']})

    def checkDate(self, field, value):
        if (isinstance(value, str) or isinstance(value, unicode)) and re.search('^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$', value):
            return True
        else:
            self.addError(field=field, errtype='format', error='Format de date incorrect')

    def checkFloat(self, field, value):
        if isinstance(value, float) or \
           ((isinstance(value, str) or isinstance(value, unicode)) and re.search('^\d+(\.\d*|)$', value)):
            return True
        else:
            self.addError(field=field, errtype='format', error='Not a floating point number')

    def checkWithin(self, field, value, min, max):
        self.checkUnder(field, value, max)
        self.checkOver(field, value, min)

    def checkOver(self, field, value, min):
        if value>min:
            return True
        else:
            self.addError(field=field, errtype='format', error='La valeur doit être supérieure à '+str(min))

    def checkUnder(self, field, value, max):
        if value<min:
            return True
        else:
            self.addError(field=field, errtype='format', error='La valeur doit être inférieure à '+str(min))

    def checkMinLength(self, field, value, length):
        if len(value)<length:
            self.addError(field=field, errtype='length', error='Il faut au moins '+str(length)+' caractères.')

    def checkEmail(self, field, value):
        if not "@" in value:
            self.addError(field=field, errtype='format', error='Cet email n''a pas de @ !')

    def maybeRaise(self):
        if len(self.errors)>0:
            raise self

app.model.ApiErrors = ApiErrors
