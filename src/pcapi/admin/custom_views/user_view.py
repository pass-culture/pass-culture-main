from wtforms import validators

from pcapi.admin.base_configuration import BaseAdminView


class UserView(BaseAdminView):
    can_edit = True
    column_list = [
        "id",
        "isBeneficiary",
        "email",
        "firstName",
        "lastName",
        "publicName",
        "dateOfBirth",
        "departementCode",
        "phoneNumber",
        "postalCode",
        "resetPasswordToken",
        "validationToken",
    ]
    column_labels = dict(
        email="Email",
        isBeneficiary="Est bénéficiaire",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        phoneNumber="Numéro de téléphone",
        postalCode="Code postal",
        resetPasswordToken="Jeton d'activation et réinitialisation de mot de passe",
        validationToken="Jeton de validation d'adresse email",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["postalCode", "isBeneficiary"]
    form_columns = [
        "email",
        "firstName",
        "lastName",
        "publicName",
        "dateOfBirth",
        "departementCode",
        "postalCode",
        "isBeneficiary",
    ]

    def on_model_change(self, form, model, is_created):
        # If a user is a pro or an admin, he shouldn't be able to book offers
        if form.isBeneficiary.data and (model.isAdmin or len(model.offerers) > 0):
            raise validators.ValidationError("Seul un jeune peut réserver des offres")

        super().on_model_change(form, model, is_created)
