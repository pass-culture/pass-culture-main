# Generic single-database configuration

1. Se mettre à jour avec l'état de migration

```bash
pc alembic stamp head
```

2. Créér un fichier boilerplate de la nouvelle migration

```bash
pc alembic revision -m "nom_de_la_revision"
```

3. Une fois la fonction upgrade remplie

```bash
pc alembic upgrade <id>
```

## Do 

Il est possible d'effectuer une migration soit par des commandes SQL : 

```SQL
ALTER TABLE "booking" ADD COLUMN amount numeric(10,2);
```

soit par les fonctions fournies par la bibliothèque alembic:


```python
op.add_column('venue_provider', sa.Column('syncWorkerId', sa.VARCHAR(24), nullable=True))
```

## Don't

Lorsque vous souhaitez modifier la structure de plusieurs tables en même temps, 
il ne faut pas utiliser la même transaction pour l'ensemble.

Eviter de faire:

```python
op.add_column('stock', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
op.add_column('offer', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
```

Mais faire plutôt:
 
```python
 op.add_column('stock', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
    op.add_column('offer', sa.Column('fieldsUpdated', sa.ARRAY(sa.String(100)), nullable=False, server_default="{}"))
    op.execute("COMMIT")
```

Si on utilise la même transaction on risque d'avoir ce genre d'erreurs sur Scalingo:
```
sqlalchemy.exc.OperationalError: (psycopg2.extensions.TransactionRollbackError) deadlock detected
```