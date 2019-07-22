from flask_admin.helpers import get_form_data
from flask_login import current_user
from wtforms import Form, SelectField, StringField

from admin.base_configuration import BaseAdminView
from domain.user_activation import is_import_status_change_allowed, IMPORT_STATUS_MODIFICATION_RULE
from models import ImportStatus, PcObject


class OffererAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'name', 'siren', 'city', 'postalCode', 'address']
    column_labels = dict(name='Nom', siren='SIREN', city='Ville', postalCode='Code postal', address='Adresse')
    column_searchable_list = ['name', 'siren']
    column_filters = ['postalCode', 'city']
    form_columns = ['name', 'siren', 'city', 'postalCode', 'address']


class UserAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'canBookFreeOffers', 'email', 'firstName', 'lastName', 'publicName', 'dateOfBirth',
                   'departementCode', 'postalCode', 'resetPasswordToken', 'validationToken']
    column_labels = dict(
        email='Email', canBookFreeOffers='Peut réserver', firstName='Prénom', lastName='Nom',
        publicName="Nom d'utilisateur",
        dateOfBirth='Date de naissance', departementCode='Département', postalCode='Code postal',
        resetPasswordToken='Jeton d\'activation et réinitialisation de mot de passe',
        validationToken='Jeton de validation d\'adresse email'
    )
    column_searchable_list = ['publicName', 'email', 'firstName', 'lastName']
    column_filters = ['postalCode', 'canBookFreeOffers']
    form_columns = ['email', 'firstName', 'lastName', 'publicName', 'dateOfBirth', 'departementCode', 'postalCode']


class VenueAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'name', 'siret', 'city', 'postalCode', 'address', 'publicName', 'latitude', 'longitude']
    column_labels = dict(name='Nom', siret='SIRET', city='Ville', postalCode='Code postal', address='Adresse',
                         publicName='Nom d\'usage', latitude='Latitude', longitude='Longitude')
    column_searchable_list = ['name', 'siret', 'publicName']
    column_filters = ['postalCode', 'city', 'publicName']
    form_columns = ['name', 'siret', 'city', 'postalCode', 'address', 'publicName', 'latitude', 'longitude']


class FeatureAdminView(BaseAdminView):
    can_edit = True
    column_list = ['name', 'description', 'isActive']
    column_labels = dict(name='Nom', description='Description', isActive='Activé')
    form_columns = ['isActive']


class BeneficiaryImportView(BaseAdminView):
    can_edit = True
    column_list = ['beneficiary.email', 'demarcheSimplifieeApplicationId', 'currentStatus', 'updatedAt', 'detail', 'authorEmail']
    column_labels = {
        'demarcheSimplifieeApplicationId': 'Dossier DMS',
        'beneficiary.email': 'Bénéficiaire',
        'currentStatus': "Statut",
        'updatedAt': "Date",
        'detail': "Détail",
        'authorEmail': 'Statut modifié par'
    }
    column_searchable_list = ['beneficiary.email', 'demarcheSimplifieeApplicationId']
    column_sortable_list = ['beneficiary.email', 'demarcheSimplifieeApplicationId', 'currentStatus', 'updatedAt',
                            'detail', 'authorEmail']

    def edit_form(self, obj=None):
        class _NewStatusForm(Form):
            beneficiary = StringField('Bénéficiaire', default=obj.beneficiary.email, render_kw={'readonly': True})
            dms_id = StringField(
                'Dossier DMS', default=obj.demarcheSimplifieeApplicationId, render_kw={'readonly': True}
            )
            detail = StringField('Raison du changement de statut')
            status = SelectField('Nouveau statut', choices=[(s.name, s.value) for s in ImportStatus])

        return _NewStatusForm(get_form_data())

    def update_model(self, form, model):
        new_status = ImportStatus(form.status.data)

        if is_import_status_change_allowed(model.currentStatus, new_status):
            model.setStatus(new_status, detail=form.detail.data, author=current_user)
            PcObject.save(model)
        else:
            form.status.errors.append(IMPORT_STATUS_MODIFICATION_RULE)
