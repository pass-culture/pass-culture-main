# Package `models`

## Typage des colonnes des modèles

### Inférence des types

- Cas 1 : Le cas nominal

  SqlAlchemy et mypy infèrent correctement le type.

  - Exemple:
    ```python
    quantity = sa.Column(sa.Integer, nullable=True) # quantity est de type int | None
    ```

- Cas 2 : le cas des colonnes non nullables

  Même si une colonne est non nullable, le type inféré par mypy est <python type> | None

  En effet, à l'instanciation de l'objet, on n'a aucune garantie que l'attribut ne soit pas `None`.
  Le remplissage de la valeur par défaut a lieu au moment du `commit` en base de donnée.

  - Exemple :
    ```python
    >> m1 = MyClass()
    >> m1.id
    None
    ```

  Dans ce cas, on choisit de considérer que le type n'est pas `None`. Les cas où l'attribut peut être `None` sont beaucoup plus rares, entre
  l'instanciation de la classe et son commit en base de données.
  :warning: Faire bien attention à ce cas lors de la création d'objets

  - Exemple :
    ```python
    subcategoryId: str = sa.Column(sa.Text, nullable=False) # subcategoryId est de type str
    ```

- Cas 3 : le cas où mypy ne sait pas inférer

  Parfois, mypy ne parvient pas à inférer de type, par exemple dans le cas d'une `relationship` entre deux tables.
  Dans ce cas il faut explicitement fournir le type.

  - Exemple :
    ```python
    product: Product = sa_orm.relationship(Product, back_populates="offers") # product est de type Product
    ```

### Quand utiliser Mapped ?

Dans certains cas, on peut avoir besoin de typer avec `sqlalchemy.orm.Mapped`.
Notamment quand on a besoin d'appliquer une fonction à l'attribut de classe (Généralement dans une query).

- Exemple:

  ```python
  import sqlalchemy.orm as sa_orm

  class Offer:
    id: sa_orm.Mapped[int] = Column(BigInteger, primary_key=True, autoincrement=True)

  Offer.query.filter(Offer.id.in_(my_list))
  ```

### Références

[https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html#usage](https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html#usage)

## Feature Flags

Les Feature Flags (ou Feature Toggle) permettent de désactiver / activer une fonctionnalité depuis l'admin (ex: [admin staging](https://backoffice.staging.passculture.team/admin/feature-flipping)) sans avoir besoin de déployer de code.

### Installer un nouveau Feature Flag

1. **Ajouter** une ligne dans l'enum `FeatureToggle`

Le flag sera ajouté dans la table `Feature` lors du déploiement, via la méthode `install_feature_flags`

2. Configurer la **valeur par défaut** (ou initiale) du flag.

Si la valeur initiale est `True`, ne rien faire.

Si la valeur initiale est `False`, ajouter une ligne dans le tuple `FEATURES_DISABLED_BY_DEFAULT`.

3. ⚠️ Dans le cas d'utilisation _ajout d'une fonctionnalité activée une fois que les développements sont finis_, **créer un ticket** pour supprimer le feature flag, ou a mininima pour modifier sa valeur initiale, une fois le chantier fini. En effet, cela peut avoir un impact sur :

- la qualité des tests : c'est la valeur par défaut qui est utilisée (sauf si `@pytest.mark.features` est utilisé)
- les bugs sur l'environnement `testing` : les données sont périodiquement regénérées et les Feature Flag sont alors réinitialisés avec leur valeur par défaut.

### Transmettre un Feature Flag à l'app jeune

Lorsqu'on a besoin d'utiliser un Feature Flag sur l'app jeune, il faut transmettre le Feature Flag via l'endpoint [`/settings`](https://github.com/pass-culture/pass-culture-main/blob/d4eeed54c82aa616f10473198518b636c8e19d3c/api/tests/routes/native/v1/settings_test.py#L24).

Pour que cet ajout soit mis à disposition dans le contrat d'interface généré par Swagger pour l'app native, il faut également l'ajouter à la classe de SettingsResponse dans le serializer de settings.py.

### Supprimer un Feature Flag

1. Enlever toute utilisation du flag
2. Enlever la ligne de FeatureToggle
3. Pour les environnements locaux et/ou hors Docker, `flask clean_data` supprimera les FF qui sont en base mais ne sont plus utilisées. Dans les environnements déployés, la commande est automatiquement lancée en fin de déploiement.