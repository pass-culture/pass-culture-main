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
