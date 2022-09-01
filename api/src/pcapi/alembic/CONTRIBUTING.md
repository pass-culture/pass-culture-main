# Générer un fichier de migration

⚠️ Les migrations peuvent engendrer des interruptions de service lors des déploiements.

Pour effectuer une migration du schéma de la base de données, il est recommandé d'effectuer les étapes suivantes :

### 1. Modifier le modèle applicatif dans les fichiers python

### 2. Identifier s'il s'agit d'un migration `pre` ou `post`

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

## Autres commandes utiles :

- Afficher le sql généré entre 2 migrations sans la jouer

```
pc alembic upgrade e7b46b06f6dd:head --sql
```

## Do/Don't

### Do

Il est possible d'effectuer une migration soit par des commandes SQL :

```SQL
ALTER TABLE "booking" ADD COLUMN amount numeric(10,2);
```

soit par les fonctions fournies par la bibliothèque alembic:

```python
op.add_column('venue_provider', sa.Column('syncWorkerId', sa.VARCHAR(24), nullable=True))
```
