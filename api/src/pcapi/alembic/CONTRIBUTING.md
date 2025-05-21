# Générer un fichier de migration

⚠️ Les migrations peuvent engendrer des interruptions de service lors des déploiements.

Pour effectuer une migration du schéma de la base de données, il est recommandé d'effectuer les étapes suivantes :

## 1. Modifier le modèle applicatif dans les fichiers python

## 2. Identifier s'il s'agit d'une migration `pre` ou `post`

Lors d'un déploiement, on part d'un état stable (version `N` des migrations / version `N` du code) vers un autre état stable (version `N+1` des migrations / version `N+1` du code) en passant par 3 phases :

1. Migrations `pre` : les migrations qui sont compatibles avec le code N (exemple : ajout de colonne)
2. Déploiement du code version `N+1`, compatible avec les migrations `pre`
3. Migrations `post` : les migrations qui ne sont pas compatibles avec le code version `N` (exemple : suppression de colonne) mais compatibles avec le code version `N+1`

Le code doit être stable pendant ces 3 phases.

Il donc est primordial de se poser la question suivante : est-ce que ma migration `N+1` est compatible avec le code version `N` ?

Si oui, il s'agit d'une migration `pre`. Si non, il s'agit d'une migration `post`.

Note : La phase 1 peut durer longtemps. Par exemple si une des migrations échoue, le code `N+1` n'est pas déployé alors qu'une partie des migrations `pre` peut être passée. Helm timeout sur les commandes durant plus de 5 minutes, ce qui fait échouer le déploiement.

## 3. Générer le fichier de migration

Pour une migration `pre`

```bash
pc alembic  revision --head pre@head -m nom_de_la_migration
```

Pour une migration `post`

```bash
pc alembic  revision --head post@head -m nom_de_la_migration
```

On peut générer une migration de manière automatique en ajoutant le flag `--autogenerate`.

Par exemple :

```bash
pc alembic revision -m nom_de_la_migration --autogenerate --head pre@head
```

Note : alembic peut ne pas détecter automatiquement les différences entre le modèle et la base de donnée [cf la doc autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).
Le projet est configuré pour ignorer les suppressions de tables et les actions sur les colonnes `TEXT` contenant des `Enum` dans l'auto-génération.

## 4. Lire le fichier de migration généré et enlever les commentaires

## 5. Jouer la migration 

Dans le cas d'une modification `pre`

```bash
pc alembic upgrade pre@head
```

Dans le cas d'une modification `post`

```bash
pc alembic upgrade post@head
```

## 6. Tester la fonction de downgrade (sur les migrations de chaque branche)

```bash
pc alembic downgrade pre@-1
pc alembic downgrade post@-1

```

## 7. Mettre à jour le fichier alembic_version_conflict_detection.txt

[Ce fichier](../../../alembic_version_conflict_detection.txt) contient les numéros des dernières migrations pre et post du code.

Il permet de générer un conflit git lorsqu'un commit ajoutant une migration a été poussé sur la branche visée et n'est pas présent sur la branche courante.

La mise à jour de ce fichier est en principe automatiquement effectuée par un hook de pre-commit.

En cas de conflit, un script existe pour rebase les migrations : `bin/alembic_rebase_migrations.py`.

Sinon il faut :
1. Downgrade les nouvelles migrations avant de rebase.
2. Rebase sur `origin/master`.
3. Remplacer le `down_revision` de la première migration `pre` et `post` par leur tête sur `origin/master`, qui est défini dans le `alembic_version_conflict_detection.txt` de `origin/master`.
4. Tester les nouvelles migrations avec `alembic upgrade`.
5. Remplacer les têtes de `alembic_version_conflict_detection.txt` par les nouvelles versions.

## Autres commandes utiles

Afficher le sql généré entre 2 migrations sans la jouer

```
pc alembic upgrade e7b46b06f6dd:head --sql
```

# Standards

## Format de la migration

Il est possible d'effectuer une migration soit par des commandes SQL :

```SQL
ALTER TABLE "booking" ADD COLUMN amount numeric(10,2);
```

soit par les fonctions fournies par la bibliothèque alembic:

```python
op.add_column('venue_provider', sa.Column('syncWorkerId', sa.VARCHAR(24), nullable=True))
```

## Typage

Pour un meilleur typage des colonnes de type "ARRAY", utiliser `sqlalchemy.dialects.postgresql.ARRAY` plutôt que `sqlalchemy.typing`.

## Lint et zero downtime deployments

[squawk](https://github.com/sbdchd/squawk/) est utilisé afin d'attraper les migrations dangereuses qui verrouillent la base de donnée, empêchant les lectures/écritures et donc créant du downtime applicatif.

Pour désactiver le lint sur une seule expression SQL, le commentaire `-- squawk:ignore-next-statement` doit être placé juste avant :

```python
def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(sql_statement_that_would_upset_squawk)
```

Note : le `select 1` permet d'éviter une requête vide, ce que SQLAlchemy n'apprécie pas du tout.

Attention : Ne pas ajouter de lignes vides à la fin du fichier alembic_version_conflict_detection.txt. L'ajout entraînera l'échec de l'étape de lint dans la CI sur la branche master une fois la pull request mergée.
Si une ligne vide est ajoutée par erreur, il est nécessaire de merger une correction sur master, même si la CI échoue pour la pull request concernée.

### Migrations inoffensives

Ces migrations ne créeront (quasiment) pas de temps mort pour PostgreSQL 15.

#### Ajout d'une colonne nullable

À écrire dans une migration *pre* :

```python
op.add_column("venue", sa.Column("street", sa.Text(), nullable=True))
```

#### Ajout d'une colonne non-nullable avec une valeur constante par défaut

À écrire dans une migration *pre* :

```python
op.add_column("product", sa.Column("isGcuCompatible", sa.BOOLEAN(), server_default=sa.text("true"), nullable=False))
```

Note : La valeur constante, ou non-volatile d'après le jargon PostgreSQL, est essentielle pour que cette migration soit inoffensive. `true`, `1` ou `''` sont des valeurs constantes, mais `now()` ne l'est pas.

#### Ajout d'une valeur par défaut dans une colonne

À écrire dans une migration *pre* :

```python
op.alter_column(
    'offer_report',
    'reportedAt',
    existing_type=postgresql.TIMESTAMP(),
    server_default=sa.text('now()'),
)
```

La valeur par défaut ne va pas remplir la colonne des lignes existantes, que celles des futures lignes.

#### Suppression d'une colonne nullable

À écrire dans une migration *post* :

```python
op.drop_column("product", "isGcuCompatible")
```

#### Ajout d'une table

À écrire dans une migration *pre* :

```python
op.create_table(
    "gdpr_user_data_extract",
    sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
)
```

#### Suppression d'une table

À écrire dans une migration *post* :

```python
op.drop_table("gdpr_user_data_extract")
```

#### Suppression d'une contrainte

À écrire dans une migration *pre* si elle n'est pas compatible avec le code N+1, sinon *post* :

```python
op.drop_constraint("pricing_eventId_not_null_constraint", table_name="pricing")
```

Note : En théorie, la suppression d'une contrainte est dangereuse parce qu'elle verrouille exclusivement la table. 
En pratique, la suppression d'une contrainte est très rapide, beaucoup plus que l'attente d'obtention du verrou.

### Migrations dangereuses

Ces migrations verrouillent la base de donnée en lecture/écriture si elles sont écrites de manière naïves.

❓ L'obtention du verrou d'une table peut être longue, par exemple s'il y a un fort volume de requêtes SQL et/ou des requêtes longues. Si c'est très long, ça peut même échouer, selon la valeur du "lock timeout". Toutes les requêtes SQL qui sont effectuées après la demande de lock (et avant sa libération) s'empilent sans être traitées par PostgreSQL. Donc si le lock met 3 minutes à être pris, ça veut dire qu'on va empiler toutes les requêtes (y compris de simples `select`) pendant 3 minutes. 

Si on timeout, toutes les requêtes échouent avec une erreur 500. Si on ne timeout pas via un "lock timeout" plus long, alors les requêtes ont des chances de finir par être exécutées, mais on aura explosé la charge sur Gunicorn parce que toutes les requêtes vont prendre plusieurs minutes. Certaines requêtes HTTP ne pourront pas être servies, et retourneront des erreurs 503 en masse.


#### Ajout d'une colonne non-nullable sans valeur constante par défaut

❌ Ne fonctionnera pas entre la migration *pre* et le déploiement du code N+1 :

```python
op.add_column('offer', sa.Column('foo', sa.Text(), nullable=False))
```

❓ Il existe une fenêtre de temps où la migration pre est effectuée mais le code N+1 n'est pas déployé. Dans cette fenêtre, il est possible d'écrire une ligne avec la colonne `foo` nulle parce que le code N n'a pas connaissance de cette colonne, ce qui entraîne une erreur d'intégrité en base de donnée.

✅ Deux déploiements doivent être réalisés, donc deux migrations *pre* doivent être écrites :

```python
op.add_column('offer', sa.Column('foo', sa.Text(), nullable=True))
```

Le code N+1 doit écrire la colonne `foo` qui peut être peuplée via une migration *post* du premier déploiement. 
Après assurance qu'il n'existe pas de ligne pour laquelle `foo` soit nulle, alors la deuxième migration *pre* peut être écrite :

```python
op.alter_column('offer', sa.Column('foo', sa.Text(), nullable=False))
```

Note : Cette manière de rendre la colonne non-nullable n'est possible que si la table ne contient que peu de lignes (< 1 million). 
Si la table est trop grosse (> 1 million de lignes), il faut [passer par un utilitaire](/api/bin/alembic_add_not_null_constraint.py) qui génère les 4 migrations nécessaires.

#### Déplacement d'une colonne d'une table vers une autre table

❌ Ne fonctionnera pas entre la migration *pre* et le déploiement du code N+1 :

```python
# pre/post deployment: pre
def upgrade() -> None:
    op.add_column("allocine_venue_provider", sa.Column("price", sa.Numeric(precision=10, scale=2)))

# pre/post deployment: post
def upgrade() -> None:
    op.execute(backfill_data_from_a_table_to_another)
    op.drop_column("allocine_venue_provider_price_rule", "price")

# in the N+1 code, all the reads/writes go from allocine_venue_provider_price_rule.price to allocine_venue_provider.price
```

❓ Il existe une fenêtre de temps où la migration pre est effectuée mais le code N+1 n'est pas déployé. Dans cette fenêtre, il est possible d'écrire un `allocine_venue_provider` sans `price` parce que le code N n'a pas connaissance de cette colonne, ce qui entraîne un trou dans la raquette.

✅ Deux déploiements doivent être réalisés :

```python
# first deployment
# pre/post deployment: pre
def upgrade() -> None:
    op.add_column("allocine_venue_provider", sa.Column("price", sa.Numeric(precision=10, scale=2)))

# in the N+1 code, allocine_venue_provider_price_rule.price is read and both columns are written

# pre/post deployment: post
def upgrade() -> None:
    op.execute(backfill_data_from_a_table_to_another)
```

```python
# in the N+2 code, all reads and writes are done in the new table

# second deployment
# pre/post deployment: post
def upgrade() -> None:
    op.drop_column("allocine_venue_provider_price_rule", "price")
```

Note : Déplacer une colonne de table ou renommer une colonne se comportent de la même manière.

#### Suppression d'une colonne non-nullable

❌ Ne fonctionnera pas ni dans une migration *pre* ou entre le déploiement du code N+1 et la migration *post* :

```python
op.drop_column("offer", "isDuo")
```

❓ Il existe une fenêtre de temps où le code N+1 est déployé mais la migration post n'est pas effectuée. Dans cette fenêtre, il est possible d'écrire un `offer` sans `isDuo` ce qui entraîne une erreur d'intégrité parce que la base de donnée s'attend à ce que `isDuo` soit encore non-nulle.

✅ Il faut d'abord [supprimer la contrainte de non-nullité](#suppression-d-une-contrainte) puis [supprimer la colonne](#suppression-d-une-colonne-nullable).

#### Ajout d'une contrainte

❌ Risque de timeout si la table `stock` contient beaucoup (> 1 million) de lignes :

```python
op.create_foreign_key(
    "stock_offererAddressId_fkey",
    "stock",
    "offerer_address",
    ["offererAddressId"],
    ["id"],
)
```

❓ Ajouter une contrainte valide verrouille exclusivement la table, empêchant toute lecture et écriture en plus du risque de timeout. De plus, pour une contrainte de clé étrangère, alors un verrou supplémentaire est pris sur la table cible. Si la table cible est fréquemment utilisée alors la prise du verrou peut échouer.

✅ La création et la validation de la contrainte doivent être séparées dans une ou plusieurs migrations *post*. La création de la contrainte non-valide assure que la contrainte est respectée pour les nouvelles lignes mais pas les anciennes. La validation de la contrainte pour les lignes existantes se fait dans un second temps.

```python
op.create_foreign_key(
    "stock_offererAddressId_fkey",
    "stock",
    "offerer_address",
    ["offererAddressId"],
    ["id"],
    postgresql_not_valid=True,
)

# make sure that the constraint is enforced for all the existing table lines 

op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
op.execute("""ALTER TABLE stock VALIDATE CONSTRAINT "stock_offererAddressId_fkey" """)
op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
```

Note : [Un utilitaire](/api/bin/alembic_add_not_null_constraint.py) existe pour générer automatiquement les 4 migrations nécessaires pour l'ajout d'une contrainte de non-nullité.

#### Ajout d'une contrainte d'unicité

❌ Risque de timeout si la table `Reaction` contient beaucoup (> 1 million) de lignes :

```python
# in models.py file
class Reaction(BaseModel):
    __table_args__ = sa.UniqueConstraint("userId", "offerId", "productId"),
```

❓ Ajouter une contrainte valide verrouille exclusivement la table, empêchant toute lecture et écriture en plus du risque de timeout. Voir [la documentation de Squawk](https://squawkhq.com/docs/disallowed-unique-constraint/)

✅ La contrainte d'unicité peut être réalisée via [un ajout d'index unique](#ajout-d-index)

```python
# in models.py file
class Reaction(BaseModel):
    __table_args__ = sa.Index("userId", "offerId", "productId", unique=True),

# in migration file
with op.get_context().autocommit_block():
    op.create_index(
        op.f("reaction_offer_product_user_unique_constraint"),
        "reaction",
        ["userId", "offerId", "productId"],
        unique=True,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
```

#### Ajout d'index

❌ Ajouter un index verrouille la table en empêchant toute écriture :

```python
op.create_index(
    op.f("ix_venue_offererAddressId"),
    "venue",
    ["offererAddressId"],
    unique=False,
    if_not_exists=True,
)
```

✅ La création d'un index doit être faite en dehors d'une transaction et de manière concurrente dans une migration *post* :

```python
with op.get_context().autocommit_block():
    op.execute("SET SESSION statement_timeout='300s'")  # or more if needed
    op.create_index(
        op.f("ix_venue_offererAddressId"),
        "venue",
        ["offererAddressId"],
        unique=False,
        if_not_exists=True,
        postgresql_concurrently=True,
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
```

#### Suppression d'index

❌ Supprimer un index verrouille exclusivement la table, empêchant toute lecture et écriture :

```python
op.drop_index(
    op.f("ix_venue_offererAddressId"), table_name="venue", if_exists=True
)
```

✅ La suppression d'un index doit être faite en dehors d'une transaction et de manière concurrente dans une migration *post* :

```python
with op.get_context().autocommit_block():
    op.drop_index(
        op.f("ix_venue_offererAddressId"), table_name="venue", postgresql_concurrently=True, if_exists=True
    )
```

# Squasher les migrations

## Objectif

Cela permet de diminuer le temps de démarrage du back et de nettoyer le code mort.
Cela consiste à regrouper toutes ces migrations dans le fichier d'initialisation de la base de donnée : `schema_init.sql`

## Comment

- Créer une nouvelle branche à partir de `production`
- Supprimer toutes les données locales, par exemple en supprimant les volumes: `docker rm -f pc-postgres && docker volume rm pass-culture-main_postgres_data`
- Lancer le backend pour initialiser la base de donnée dans l'état visé (avec toutes les migrations, et sans les données): `pc start-backend`
- Effectuer un dump la base de donnée: `docker exec pc-postgres pg_dump --inserts pass_culture -U pass_culture > /tmp/pass_culture.sql`
- Copier le fichier généré à la place de `shema_init.sql` : `cp /tmp/pass_culture.sql api/src/pcapi/alembic/versions/sql/schema_init.sql`
- Modifier le nouveau fichier `shema_init.sql`:
  - supprimer toute référence à la table `alembic_version`: alembic va s'occuper de créer cette table
  - supprimer les `ALTER TEXT SEARCH CONFIGURATION public.french_unaccent`: cette configuration est effectuée dans `install_database_extensions`, qu'on pourra supprimer dans une amélioration future
    - supprimer toutes les lignes contenant `OWNER TO pass_culture`
  - Ajouter `reset search_path;` en fin de `schema_init.sql`
- Supprimer tous les fichiers de migration jusqu'au fichiers `pre` et `post` qui été exécutés en derniers en production.
  - On peut les déterminer en se plaçant sur la branche production, dans `alembic_version_conflict_detection.txt`
- Conserver aussi `xxx_init_db.py`
- Remplacer le contenu des méthodes downgrade et upgrade des dernières migrations (pre et post) par `pass`.
- Préciser branch_labels = ("post",) ou branch_labels = ("pre",)
- Changer la down revision des deux HEAD pour pointer vers init_db
- Rebase la branche sur master

# Tester le bon fonctionnement

## Vérifier le bon fonctionnement de la base de donnée

- Supprimer la db : `docker rm -f pc-postgres && docker volume rm pass-culture-main_postgres_data`
- Lancer le backend : `pc start-backend` et s'assurer que la base de donnée s'initialise bien sans erreurs

## Vérifier le bon fonctionnement de la base de donnée de tests

- Lancer un test : `pc test-backend <nom du fichier>`
- S'assurer que la base de donnée de test s'initialise sans erreurs et que le test passe
