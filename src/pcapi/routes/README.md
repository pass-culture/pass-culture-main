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

Dans votre terminal pass Culture :

`pc alembic revision -m "nom_de_votre_migration"`

Dans le fichier de migration créée par la commande dans le répertoire alembic/versions

```python
"""le_nom_de_votre_migration

Revision ID: b25450206c2b
Revises: ba456c84727a
Create Date: 2020-03-05 16:09:44.899250

"""

from pcapi.models import feature

# revision identifiers, used by Alembic.
revision = 'b25450206c2b'
down_revision = 'ba456c84727a'
branch_labels = None
depends_on = None


FLAG = feature.FeatureToggle.ENABLE_PHONE_VALIDATION


def upgrade() -> None:
    feature.add_feature_to_database(FLAG)


def downgrade() -> None:
    feature.remove_feature_from_database(FLAG)
```

Les étapes sont normalement finies, pour vérifier :

- Relancer le backend
- Vérifier que le downgrade de la migration marche avec

```bash
pc alembic stamp id_de_votre_revision_alembic
pc alembic downgrade id_de_la_precedente_revision
```

- Vérifier que l'upgrade de la migration marche avec

```bash
pc alembic upgrade id_de_votre_revision_alembic
```
