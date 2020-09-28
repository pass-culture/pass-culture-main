# pass-culture-api

[![Coverage Status](https://coveralls.io/repos/github/betagouv/pass-culture-api/badge.svg)](https://coveralls.io/github/betagouv/pass-culture-api)

C'est le backend de l'application Pass Culture.

Il faut aller voir le README dans https://github.com/betagouv/pass-culture-main
pour être informé des différentes lignes de commande associées à ce repo.

## Lancement des tests dans un environement virtuel:

```bash
virtualenv pass-culture-api
pip install -r requirements.txt
```

Lancer postgres et redis via docker-compose (par exemple):
```bash
docker-compose -f ../docker-compose-app.yml up -d postgres-test redis
```

Lancer les tests:
```bash
pytest
```
