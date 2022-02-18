# Générer un fichier de migration

⚠️ Les migrations peuvent engendrer des interruptions de service lors des déploiements.

Pour effectuer une migration du schéma de la base de données, il est recommandé d'effectuer les étapes suivantes :

### 1. Modifier le modèle applicatif dans les fichiers python

### 2. Générer la migration de manière automatique

⚠️ Attention à ne pas avoir de contrainte `NOT NULL` au moment du lancement de la commande : 

```bash
pc alembic  revision --autogenerate --head pre@head -m nom_de_la_migration
```

Pour générer automatiquement les migrations après l'ajout de contrainte `NOT NULL`

```bash
pc alembic  revision --autogenerate --head post@head -m nom_de_la_migration
```

Si [alembic ne détecte pas automatiquement les différences entre le modèle et la db](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect), générer un fichier vide : 

#### 2.1 Sans contrainte `NOT NULL` : 
```bash
pc alembic revision -m nom_de_la_migration --head pre@head.
```
#### 2.2 AVEC contrainte `NOT NULL` :
```bash
pc alembic revision -m nom_de_la_migration --head post@head.
```

### 3. Lire le fichier de migration généré et enlever les commentaires "please adjust"

### 4. Jouer la migration :

#### 4.1. Dans le cas d'une modification qui n'est pas une contrainte `NOT NULL` ou d'un remplissage de données : 

```bash
pc alembic upgrade pre@head
```
#### 4.1. Si on veut ajouter une contrainte `NOT NULL` ou remplir une nouvelle colonne :
```bash
pc alembic upgrade post@head
```

### 5. Tester la fonction de downgrade

```bash
pc alembic downgrade -1
```

## Autres commandes utiles :

- Afficher le sql généré entre 2 migrations sans la jouer : `pc alembic upgrade e7b46b06f6dd:head --sql`

### Do

Il est possible d'effectuer une migration soit par des commandes SQL :

```SQL
ALTER TABLE "booking" ADD COLUMN amount numeric(10,2);
```

soit par les fonctions fournies par la bibliothèque alembic:

```python
op.add_column('venue_provider', sa.Column('syncWorkerId', sa.VARCHAR(24), nullable=True))
```

### Don't

Lorsque vous souhaitez modifier la structure de plusieurs tables en même temps,
il ne faut pas utiliser la même transaction pour l'ensemble.

Eviter de faire :

```python
op.add_column('stock', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
op.add_column('offer', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
```

Mais faire plutôt :

```python
op.add_column('stock', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
op.execute("COMMIT")
op.add_column('offer', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
op.execute("COMMIT")
```

Si on utilise la même transaction on risque d'avoir ce genre d'erreurs :

```
sqlalchemy.exc.OperationalError: (psycopg2.extensions.TransactionRollbackError) deadlock detected
```
