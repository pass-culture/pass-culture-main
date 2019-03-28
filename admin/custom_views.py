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
    column_list = ['id', 'canBookFreeOffers', 'email', 'firstName', 'lastName', 'publicName', 'dateOfBirth', 'departementCode', 'postalCode', 'resetPasswordToken', 'validationToken']
    column_labels = dict(
        email='Email', canBookFreeOffers='Peut réserver', firstName='Prénom', lastName='Nom', publicName="Nom d'utilisateur",
        dateOfBirth='Date de naissance', departementCode='Département', postalCode='Code postal',
        resetPasswordToken='Jeton d\'activation et réinitialisation de mot de passe', validationToken='Jeton de validation d\'adresse email'
    )
    column_searchable_list = ['publicName', 'email', 'firstName', 'lastName']
    column_filters = ['postalCode', 'canBookFreeOffers']
    form_columns = ['firstName', 'lastName', 'publicName', 'dateOfBirth', 'departementCode', 'postalCode']

class VenueAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'name', 'siret', 'city', 'postalCode', 'address']
    column_labels = dict(name='Nom', siret='SIRET', city='Ville', postalCode='Code postal', address='Adresse')
    column_searchable_list = ['name', 'siret']
    column_filters = ['postalCode', 'city']
    form_columns = ['name', 'siret', 'city', 'postalCode', 'address']