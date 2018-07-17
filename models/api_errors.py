""" api errors """
# coding=utf-8


class ApiErrors(Exception):
    def __init__(self):
        self.errors = {}

    def addError(self, field, error):
        self.errors[field] = self.errors[field].append(error)\
                                if field in self.errors\
                                else [error]

    def checkDate(self, field, value):
        if (isinstance(value, str) or isinstance(value, unicode)) and re.search('^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$', value):
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
        if value>min:
            return True
        else:
            self.addError(field, 'La valeur doit être supérieure à '+str(min))

    def checkUnder(self, field, value, max):
        if value<min:
            return True
        else:
            self.addError(field, 'La valeur doit être inférieure à '+str(min))

    def checkMinLength(self, field, value, length):
        if len(value)<length:
            self.addError(field, 'Vous devez saisir au moins '+str(length)+' caractères.')

    def checkEmail(self, field, value):
        if not "@" in value:
            self.addError(field, 'L''e-mail doit contenir un @.')

    def maybeRaise(self):
        if len(self.errors)>0:
            raise self

    status_code = None
