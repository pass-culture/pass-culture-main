# Package `admin`

Ce package sert à configurer la librairie `flask-admin`.
On trouvera dans le module `base_configuration` la classe `BaseAdminView` qui centralise la configuration commune à toutes
nos vues d'administration ainsi que le contrôle d'accès.

## Do

Si le besoin est de rajouter une nouvelle vue d'aministration, il faudra créer une nouvelle classe qui hérite de `BaseAdminView`
et qui définit les possibilités qu'elle offre à l'utilisateur : les champs visibles, éditables, filtrables, recherchables, etc.
Ces classes seront définies dans le module `custom_views`.

Par exemple :

```python
class OffererAdminView(BaseAdminView):
    can_edit = True
    column_list = ['id', 'name', 'siren', 'city', 'postalCode', 'address']
    column_labels = dict(name='Nom', siren='SIREN', city='Ville', postalCode='Code postal', address='Adresse')
    column_searchable_list = ['name', 'siren']
    column_filters = ['postalCode', 'city']
    form_columns = ['name', 'siren', 'city', 'postalCode', 'address']
```

## Don't

On évitera dans la mesure du possible de modifier la configuration de base définie dans `BaseAdminView`.
En particulier, on veut interdire, maintenant et pour toujours, de créer des données depuis la vue d'administration,
de les supprimer et de les exporter

Par exemple :

```python
class UserAdminView(BaseAdminView):
    can_create = True
    can_delete = True
    can_export = True
```

## Pour en savoir plus

- https://flask-admin.readthedocs.io/en/latest/
- https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
