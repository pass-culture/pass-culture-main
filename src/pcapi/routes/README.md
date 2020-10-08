# Manipulations courantes

## Feature Flipping

Les nouvelles fonctionnalités peuvent nécessiter d'être "feature flippé" afin d'être testées sur des environnements de tests et pas directement sur la prod. Cette décision est généralement prise avec les détenteurs du produit.

Pour faire un feature flipping dans l'API du pass Culture, les étapes suivantes sont nécessaires :

- Dans models/features ajouter une constante décrivant la fonctionnalité avec la description associée :

exemple :

```python
RECOMMENDATIONS_WITH_DISCOVERY_VIEW = 'Permettre aux utilisateurs d''avoir des recommandations de manière plus rapide'
```

- Dans le package routes, sur les routes qui seront mise à disposition ou non selon l'environnement :

Utiliser le décorateurs `@feature_required(FeatureToggle.{le nom de la constante de la feature dans le modele feature toggle})` sur la route "feature flippée"

Exemple :

```python
@app.route('/v2/recommendations', methods=['PUT'])
@login_required
@feature_required(FeatureToggle.RECOMMENDATIONS_WITH_DISCOVERY_VIEW)
@expect_json_datadefla route
put_recommendations_v2():
    json_keys = request.json.keys()
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
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b25450206c2b'
down_revision = 'ba456c84727a'
branch_labels = None
depends_on = None

class FeatureToggle(enum.Enum):
    LE_NOM_DE_VOTRE_FEATURE_DANS_L_ENUM_FEATURE = 'La description de votre feature dans l''enum feature'

def upgrade():
# Prendre toutes les valeurs de l'enum features (avec votre nouvelle variable feature flip)
    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED', 'RECOMMENDATIONS_WITH_DISCOVERY_VIEW')
# Prendre toutes les valeurs de l'enum features (sans votre nouvelle variable feature flip)
    previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    op.execute("""
            INSERT INTO feature (name, description, "isActive")
            VALUES ('%s', '%s', FALSE);
            """ % (FeatureToggle.LE_NOM_DE_VOTRE_FEATURE_DANS_L_ENUM_FEATURE.name, FeatureToggle.LE_NOM_DE_VOTRE_FEATURE_DANS_L_ENUM_FEATURE.value))
    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
# Prendre toutes les valeurs de l'enum features (sans votre nouvelle variable feature flip)
    new_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                  'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                  'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                  'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                  'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED')
# Prendre toutes les valeurs de l'enum features (avec votre nouvelle variable feature flip)
    previous_values = ('WEBAPP_SIGNUP', 'DEGRESSIVE_REIMBURSEMENT_RATE', 'QR_CODE',
                       'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE', 'SEARCH_ALGOLIA', 'SEARCH_LEGACY',
                       'BENEFICIARIES_IMPORT', 'SYNCHRONIZE_ALGOLIA', 'SYNCHRONIZE_ALLOCINE',
                       'SYNCHRONIZE_BANK_INFORMATION', 'SYNCHRONIZE_LIBRAIRES', 'SYNCHRONIZE_TITELIVE',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS', 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
                       'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'UPDATE_DISCOVERY_VIEW', 'UPDATE_BOOKING_USED',
                       'RECOMMENDATIONS_WITH_DISCOVERY_VIEW')

    previous_enum = sa.Enum(*previous_values, name='featuretoggle')
    new_enum = sa.Enum(*new_values, name='featuretoggle')
    temporary_enum = sa.Enum(*new_values, name='tmp_featuretoggle')

    op.execute("DELETE FROM feature WHERE name = 'LE_NOM_DE_VOTRE_FEATURE_DANS_L_ENUM_FEATURE'")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle'
               ' USING name::text::tmp_featuretoggle')
    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute('ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle'
               ' USING name::text::featuretoggle')
    temporary_enum.drop(op.get_bind(), checkfirst=False)

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
