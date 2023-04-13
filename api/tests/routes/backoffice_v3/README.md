# Lancer les tests des routes du backoffice v3

Le backoffice v3 utilise une application Flask distincte du reste d'`api`.

Pour l'instancier dans les tests des routes qui lui sont spécifiques, on utilise le marker Pytest `backoffice_v3` afin de récupérer une fixture `app` créée
par `build_backoffice_app()`

On lance alors les tests ainsi: 
```shell
pytest tests/routes/backoffice_v3/ -m 'backoffice_v3'
```