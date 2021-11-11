# Manipulations courantes

## Feature Flipping

Les nouvelles fonctionnalités peuvent nécessiter d'être "feature flippé" afin d'être testées sur des environnements de tests et pas directement sur la prod. Cette décision est généralement prise avec les détenteurs du produit.

Pour faire un feature flipping dans l'API du pass Culture, les étapes suivantes sont nécessaires :

- Dans models/features ajouter une constante décrivant la fonctionnalité avec la description associée :

exemple :

```python
WEBAPP_SIGNUP = 'Permettre aux bénéficiaires de créer un compte'
```

- Dans le package routes, sur les routes qui seront mise à disposition ou non selon l'environnement :

Utiliser le décorateurs `@feature_required(FeatureToggle.{le nom de la constante de la feature dans le modele feature toggle})` sur la route "feature flippée"

Exemple :

```python
@private_api.route("/users/signup/webapp", methods=["POST"])
@feature_required(FeatureToggle.WEBAPP_SIGNUP)
def signup_webapp():
    objects_to_save = []
    check_valid_signup_webapp(request)

    new_user = User(from_dict=request.json)
    ... code de la route
```

Les fonctionnalités "feature flippées" doivent être activées ou désactivées par les détenteurs du produit. Ils peuvent le faire grâce à l'interface Flask Admin. La table "feature" en base de données stocke les fonctionnalités actives.

## Ajout de la feature en base

Ajouter une ligne dans la classe `FeatureToggle`. Si sa valeur par défaut est `False`, ajouter une ligne dans `FEATURES_DISABLED_BY_DEFAULT`.
