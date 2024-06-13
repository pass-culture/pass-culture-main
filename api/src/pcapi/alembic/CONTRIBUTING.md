# Générer un fichier de migration

⚠️ Les migrations peuvent engendrer des interruptions de service lors des déploiements.

Pour effectuer une migration du schéma de la base de données, il est recommandé d'effectuer les étapes suivantes :

### 1. Modifier le modèle applicatif dans les fichiers python

### 2. Identifier s'il s'agit d'une migration `pre` ou `post`

Lors d'un déploiement, on part d'un état stable (version `N` des migrations / version `N` du code) vers un autre état stable (version `N+1` des migrations / version `N+1` du code) en passant par 3 phases :

1. Migrations `pre` : les migrations qui sont compatibles avec le code N (exemple : ajout de colonne)
2. Déploiement du code version `N+1`, compatible avec les migrations `pre`
3. Migrations `post` : les migrations qui ne sont pas compatibles avec le code version `N` (exemple : suppression de colonne) mais compatibles avec le code version `N+1`

Le code doit être stable pendant ces 3 phases.

NB: la phase 1 peut très bien durer longtemps. Par exemple si une des migrations échoue, le code `N+1` n'est pas déployé alors qu'une partie des migrations `pre` peut être passée.

Il donc est primordial de se poser la question suivante : est-ce que ma migration `N+1` est compatible avec le code version `N` ?

Si oui, il s'agit d'une migration `pre`. Si non, il s'agit d'une migration `post`.

### 2. Générer le fichier de migration

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

NB: alembic peut ne pas détecter automatiquement les différences entre le modèle et la db [cf la doc autogenrate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).

### 3. Lire le fichier de migration généré et enlever les commentaires "please adjust"

### 4. Jouer la migration :

Dans le cas d'une modification `pre`

```bash
pc alembic upgrade pre@head
```

Dans le cas d'une modification `post`

```bash
pc alembic upgrade post@head
```

### 5. Tester la fonction de downgrade (sur les migrations de chaque branche)

```bash
pc alembic downgrade pre@-1
pc alembic downgrade post@-1

```

### 6. Mettre à jour le fichier alembic_version_conflict_detection.txt

[Ce fichier](../../../alembic_version_conflict_detection.txt) contient les numéros des dernières migrations pre et post du code.

Il permet de générer un conflit git lorsqu'un commit ajoutant une migration a été poussé sur la branche visée et n'est pas présent sur la branche courante.

La mise à jour de ce fichier est en principe automatiquement effectuée par un hook de pre-commit.

## Autres commandes utiles :

- Afficher le sql généré entre 2 migrations sans la jouer

```
pc alembic upgrade e7b46b06f6dd:head --sql
```

## Standards

### Format de la migration

Il est possible d'effectuer une migration soit par des commandes SQL :

```SQL
ALTER TABLE "booking" ADD COLUMN amount numeric(10,2);
```

soit par les fonctions fournies par la bibliothèque alembic:

```python
op.add_column('venue_provider', sa.Column('syncWorkerId', sa.VARCHAR(24), nullable=True))
```

### Typage

Pour un meilleur typage des colonnes de type "ARRAY", utiliser `sqlalchemy.dialects.postgresql.ARRAY` plutôt que `sqlalchemy.typing`.

### Lint

[squawk](https://github.com/sbdchd/squawk/) est utilisé afin d'attraper les migrations qui prennent un verrou sur la base
de donnée, empêchant les lectures/écritures et donc créant du downtime applicatif.

Pour désactiver le lint sur une seule expression SQL, le commentaire `-- squawk:ignore-next-statement` doit être placé juste avant :

```python
def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(sql_statement_that_would_upset_squawk)
```

Note : le `select 1` permet d'éviter une requête vide, ce que SQLAlchemy n'apprécie pas du tout.

Attention : Ne pas ajouter de lignes vides à la fin du fichier alembic_version_conflict_detection.txt. L'ajout entraînera l'échec de l'étape de lint dans la CI sur la branche master une fois la pull request mergée.
Si une ligne vide est ajoutée par erreur, il est nécessaire de merger une correction sur master, même si la CI échoue pour la pull request concernée.

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
- Supprimer tous les fichiers de migration jusqu'au fichiers `pre` et `post` qui été exécutés en derniers en production.
  - On peut les déterminer en se plaçant sur la branche production, dans `alembic_version_conflict_detection.txt`
- Conserver aussi `xxx_init_db.py`
- Remplacer le contenu des méthodes downgrade et upgrade des dernières migrations (pre et post) par `pass`.
- Préciser branch_labels = ("post",) ou branch_labels = ("pre",)
- Changer la down revision des deux HEAD pour pointer vers init_db
- Rebase la branche sur master

## Tester le bon fonctionnement

### Vérifier le bon fonctionnement de la base de donnée

- Supprimer la db : `docker rm -f pc-postgres && docker volume rm pass-culture-main_postgres_data`
- Lancer le backend : `pc start-backend` et s'assurer que la base de donnée s'initialise bien sans erreurs

### Vérifier le bon fonctionnement de la base de donnée de tests

- Lancer un test : `pc test-backend <nom du fichier> `
- S'assurer que la base de donnée de test s'initialise sans erreurs et que le test passe
