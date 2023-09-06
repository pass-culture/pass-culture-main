# Lancer les tests des routes du backoffice

Le backoffice utilise une application Flask distincte du reste d'`api`.

Pour l'instancier dans les tests des routes qui lui sont spécifiques, on utilise le marker Pytest `backoffice` afin de récupérer une fixture `app` créée
par `build_backoffice_app()`

On lance alors les tests ainsi: 
```shell
pytest tests/routes/backoffice/ -m 'backoffice'
```