from dataclasses import fields

from flask import Response
from flask_admin import expose

from pcapi.admin.base_configuration import BaseCustomAdminView
from pcapi.core.categories.categories import ALL_CATEGORIES
from pcapi.core.categories.categories import Category
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES
from pcapi.core.categories.subcategories import HomepageLabels
from pcapi.core.categories.subcategories import SearchGroups
from pcapi.core.categories.subcategories import Subcategory


class CategoryView(BaseCustomAdminView):
    @expose("/", methods=["GET"])
    def categories(self) -> Response:
        column_names = [field.name for field in fields(Category)]
        column_labels = {
            "id": "Nom tech de la catégorie",
        }
        return self.render(
            "admin/categories_list.html",
            categories=ALL_CATEGORIES,
            column_names=column_names,
            column_labels=column_labels,
        )


class SubcategoryView(BaseCustomAdminView):
    @expose("/", methods=["GET"])
    def subcategories(self) -> Response:
        column_names = [field.name for field in fields(Subcategory)]
        column_labels = {
            "id": "Nom tech de la sous-catégorie",
            "category_id": "Nom tech de la catégorie",
        }
        return self.render(
            "admin/subcategories_list.html",
            subcategories=ALL_SUBCATEGORIES,
            search_groups=SearchGroups,
            homepage_labels=HomepageLabels,
            column_names=column_names,
            column_labels=column_labels,
        )
