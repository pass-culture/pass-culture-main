from pcapi.admin.base_configuration import BaseAdminView


class OfferCategoryView(BaseAdminView):
    list_template = "admin/offer_categories_list.html"
    can_create = True
    can_edit = True
    can_delete = False
    column_list = ["name", "proLabel", "appLabel"]
    column_sortable_list = None
    column_filters = ["name", "proLabel", "appLabel", "isActive"]
    column_default_sort = ("name", True)
    column_labels = {
        "name": "Nom",
        "isActive": "Visible",
        "proLabel": "Nom affiché sur le portail pro",
        "appLabel": "Nom affiché sur l'app",
    }
    form_excluded_columns = ["subcategories"]
    can_export = True

    def is_accessible(self):
        return super().is_accessible() and self.check_super_admins()


class OfferSubcategoryView(BaseAdminView):
    list_template = "admin/offer_subcategories_list.html"
    can_create = True
    can_edit = True
    can_delete = False
    column_list = [
        "name",
        "category.name",
        "proLabel",
        "appLabel",
        "isEvent",
        "isDigital",
        "isDigitalDeposit",
        "isPhysicalDeposit",
        "canExpire",
        "canBeDuo",
        "conditionalFields",
        "isActive",
    ]
    column_sortable_list = ["name", "category.name", "proLabel", "appLabel"]
    column_filters = ["name", "category.name", "proLabel", "appLabel", "isActive"]
    column_default_sort = ("name", True)
    column_labels = {
        "name": "Nom de la sous-catégorie",
        "isActive": "Visible",
        "proLabel": "Nom affiché sur le portail pro",
        "appLabel": "Nom affiché sur l'app",
        "category.name": "Catégorie parente",
        "category": "Catégorie parente",
        "isEvent": "Événement",
        "canBeDuo": "Offre duo",
        "canExpire": "Avec date limite de retrait",
        "isDigital": "Offre numérique",
        "isDigitalDeposit": "Plafond numérique",
        "isPhysicalDeposit": "Plafond physique",
        "conditionalFields": "Champs additionnels",
    }
    form_columns = [
        "name",
        "isActive",
        "category",
        "proLabel",
        "appLabel",
        "isEvent",
        "canBeDuo",
        "canExpire",
        "isDigital",
        "isDigitalDeposit",
        "isPhysicalDeposit",
        "conditionalFields",
    ]
    can_export = True

    def is_accessible(self):
        return super().is_accessible() and self.check_super_admins()
