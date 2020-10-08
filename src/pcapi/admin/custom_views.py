from flask_admin.helpers import get_form_data
from flask_login import current_user
from wtforms import Form, StringField, TextAreaField, SelectField

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors import redis
from pcapi.domain.user_activation import is_import_status_change_allowed, IMPORT_STATUS_MODIFICATION_RULE
from pcapi.flask_app import app
from pcapi.models import ImportStatus, BeneficiaryImport, OfferSQLEntity
from pcapi.repository import repository


class OfferAdminView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ['id', 'name', 'type', 'criteria']
    column_searchable_list = ['name', 'criteria.name']
    column_sortable_list = ['name', 'type', 'criteria']
    column_labels = {
        'name': 'Nom',
        'type': 'Type',
        'criteria': 'Tag',
        'criteria.name': 'Tag'
    }
    column_filters = ['type', 'criteria.name']
    form_columns = ['criteria']

    def on_model_change(self, form: Form, offer: OfferSQLEntity, is_created=False):
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)


class CriteriaAdminView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = ['id', 'name', 'description', 'scoreDelta']
    column_labels = dict(name='Nom', description='Description', scoreDelta='Score')
    column_searchable_list = ['name', 'description']
    column_filters = []
    form_columns = ['name', 'description', 'scoreDelta']


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
                   'departementCode', 'phoneNumber', 'postalCode', 'resetPasswordToken', 'validationToken']
    column_labels = dict(
        email='Email', canBookFreeOffers='Peut réserver', firstName='Prénom', lastName='Nom',
        publicName="Nom d'utilisateur", dateOfBirth='Date de naissance', departementCode='Département',
        phoneNumber='Numéro de téléphone', postalCode='Code postal',
        resetPasswordToken='Jeton d\'activation et réinitialisation de mot de passe',
        validationToken='Jeton de validation d\'adresse email'
    )
    column_searchable_list = ['id', 'publicName',
                              'email', 'firstName', 'lastName']
    column_filters = ['postalCode', 'canBookFreeOffers']
    form_columns = ['email', 'firstName', 'lastName',
                    'publicName', 'dateOfBirth', 'departementCode', 'postalCode']


class VenueAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'name', 'siret', 'city', 'postalCode',
                   'address', 'publicName', 'latitude', 'longitude']
    column_labels = dict(name='Nom', siret='SIRET', city='Ville', postalCode='Code postal', address='Adresse',
                         publicName='Nom d\'usage', latitude='Latitude', longitude='Longitude')
    column_searchable_list = ['name', 'siret', 'publicName']
    column_filters = ['postalCode', 'city', 'publicName']
    form_columns = ['name', 'siret', 'city', 'postalCode',
                    'address', 'publicName', 'latitude', 'longitude']


class FeatureAdminView(BaseAdminView):
    can_edit = True
    column_list = ['name', 'description', 'isActive']
    column_labels = dict(name='Nom', description='Description', isActive='Activé')
    form_columns = ['isActive']


class BeneficiaryImportView(BaseAdminView):
    can_edit = True
    column_list = ['beneficiary.firstName', 'beneficiary.lastName', 'beneficiary.email', 'beneficiary.postalCode',
                   'source', 'sourceId', 'applicationId', 'currentStatus', 'updatedAt', 'detail', 'authorEmail']
    column_labels = {
        'applicationId': 'Id de dossier',
        'authorEmail': 'Statut modifié par',
        'beneficiary.lastName': 'Nom',
        'beneficiary.firstName': 'Prénom',
        'beneficiary.postalCode': 'Code postal',
        'beneficiary.email': 'Adresse e-mail',
        'currentStatus': 'Statut',
        'detail': 'Détail',
        'source_id': 'Id de la procédure',
        'source': 'Source du dossier',
        'updatedAt': 'Date'
    }
    column_searchable_list = ['beneficiary.email',
                              'applicationId']
    column_filters = ['currentStatus']
    column_sortable_list = ['beneficiary.email', 'beneficiary.firstName', 'beneficiary.lastName',
                            'beneficiary.postalCode', 'applicationId', 'source', 'sourceId', 'currentStatus',
                            'updatedAt', 'detail', 'authorEmail']

    def edit_form(self, obj=None):
        class _NewStatusForm(Form):
            beneficiary = StringField('Bénéficiaire', default=obj.beneficiary.email if obj.beneficiary else 'N/A',
                                      render_kw={'readonly': True})
            applicationId = StringField(
                'Dossier DMS', default=obj.applicationId, render_kw={'readonly': True}
            )
            statuses = TextAreaField('Status précédents', default=obj.history,
                                     render_kw={'readonly': True, 'rows': len(obj.statuses)})
            detail = StringField('Raison du changement de statut')
            status = SelectField('Nouveau statut',
                                 choices=[(status.name, status.value)
                                          for status in ImportStatus],
                                 default=obj.currentStatus.value)

        return _NewStatusForm(get_form_data())

    def update_model(self, new_status_form: Form, beneficiary_import: BeneficiaryImport):
        new_status = ImportStatus(new_status_form.status.data)

        if is_import_status_change_allowed(beneficiary_import.currentStatus, new_status):
            beneficiary_import.setStatus(new_status, detail=new_status_form.detail.data, author=current_user)
            repository.save(beneficiary_import)
        else:
            new_status_form.status.errors.append(IMPORT_STATUS_MODIFICATION_RULE)
