from admin.base_configuration import BaseAdminView


class OffererAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'name', 'siren', 'city', 'postalCode', 'address']
    column_labels = dict(name='Nom', siren='SIREN', city='Ville', postalCode='Code postal', address='Adresse')
    column_searchable_list = ['name', 'siren']
    column_filters = ['postalCode', 'city']
    form_columns = ['name', 'siren', 'city', 'postalCode', 'address']


class UserAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'canBookFreeOffers', 'email', 'firstName', 'lastName', 'publicName', 'dateOfBirth', 'postalCode']
    column_labels = dict(
        email='Email', firstName='Prénom', lastName='Nom', publicName="Nom d'utilsateur",
        dateOfBirth='Date de naissance', postalCode='Code postal', canBookFreeOffers='Peut réserver'
    )
    column_searchable_list = ['publicName']
    column_filters = ['postalCode', 'canBookFreeOffers']
    form_columns = ['firstName', 'lastName', 'publicName', 'dateOfBirth']
