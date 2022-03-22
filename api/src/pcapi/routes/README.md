# Manipulations courantes

## Feature Flipping

Les nouvelles fonctionnalités peuvent nécessiter d'être "feature flippé" afin d'être testées sur des environnements de tests et pas directement sur la prod. Cette décision est généralement prise avec les détenteurs du produit.

Pour faire un feature flipping dans l'API du pass Culture, les étapes suivantes sont nécessaires :

- Dans models/features ajouter une constante décrivant la fonctionnalité avec la description associée :

exemple :

```python
ENABLE_FROBULATE = 'Active la frobulation'
```

- Dans le package routes, sur les routes qui seront mise à disposition ou non selon l'environnement :

Utiliser le décorateurs `@feature_required(FeatureToggle.{le nom de la constante de la feature dans le modele feature toggle})` sur la route "feature flippée"

Exemple :

```python
@private_api.route("/users/frobulate", methods=["POST"])
@feature_required(FeatureToggle.ENABLE_FROBULATION)
def frobulate():
    ... code de la route
```

Les fonctionnalités "feature flippées" doivent être activées ou désactivées par les détenteurs du produit. Ils peuvent le faire grâce à l'interface Flask Admin. La table "feature" en base de données stocke les fonctionnalités actives.

## Ajout de la feature en base

Ajouter une ligne dans la classe `FeatureToggle`. Si sa valeur par défaut est `False`, ajouter une ligne dans `FEATURES_DISABLED_BY_DEFAULT`.

# Troubleshooting

## Ajout d'un nouveau fichier de route

Vous pouvez être amené à ajouter un nouveau fichier de routes `votre_fichier.py` pour un nouveau besoin métier. Pour que ces routes du nouveau fichier soient exposées et, par conséquent, pour les voir apparaître dans votre interface de routes (swagger, par exemple), il faut bien s'assurer que ce fichier soit initialisé dans le fichier `__init__.py` situé au même niveau dans l'arborescence de fichiers.
