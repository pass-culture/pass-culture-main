# Package `admin`

Ce package sert à configurer la librairie `flask-admin` utilisée pour le backoffice.

Ce backoffice est remplacé par une autre application (backofficev3).

On trouvera dans le module `base_configuration` la classe `BaseAdminView` qui centralise la configuration commune à toutes
nos vues d'administration ainsi que le contrôle d'accès.

## Afficher la page Flask Admin en local

1. Récupérer les 2 variables suivantes sur la Console Google

- [pcapi-testing_google_client_id](https://console.cloud.google.com/security/secret-manager/secret/pcapi-testing_google_client_id/versions?project=passculture-metier-ehp)
- [pcapi-testing_google_client_secret](https://console.cloud.google.com/security/secret-manager/secret/pcapi-testing_google_client_secret/versions?project=passculture-metier-ehp)

On peut aussi se connecter au pod testing

```
pc -e testing python
print(pcapi.settings.GOOGLE_CLIENT_SECRET, pcapi.settings.GOOGLE_CLIENT_ID)
```

2. Overrider les valeurs de ces variables dans le `.env.local.secret` du projet (créer le fichier s'il n'existe pas).

```
GOOGLE_CLIENT_ID=client-id
GOOGLE_CLIENT_SECRET=client-secret
```

3. Se rendre sur `http://localhost/pc/back-office` et se connecter avec l'OAuth Google.

## Standards

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


## Documentation flask-admin

- https://flask-admin.readthedocs.io/en/latest/
- https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView
