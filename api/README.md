# pass-culture-api

[![Coverage Status](https://coveralls.io/repos/github/betagouv/pass-culture-api/badge.svg?branch=master)](https://coveralls.io/github/betagouv/pass-culture-api?branch=master)

Voici le backend de l'application Pass Culture; il est lancé via `docker-compose` en utilisant le fichier
`docker-compose-app.yml` du répertoire parent de `api`: `pass-culture-main`.

Plus de détails sur le lancement de l'infra docker-compose sont accessibles dans le
[README de pass-culture-main](https://github.com/pass-culture/pass-culture-main#readme)

## OpenAPI

Une documentation Swagger des APIs est générée selon l'OpenAPI Specification (OAS3) grâce à un schéma généré par
Spectree:

* [API Contremarque](https://backend.passculture.app/v2/swagger)
* [App Native](https://backend.passculture.app/v2/swagger)
* [Adage](https://backend.passculture.app/adage-iframe/swagger)
* [API privée et API publique dépréciée](https://backend.passculture.app/apidoc/swagger)

## Tests

### Installation des dépendances

Avec `venv` (vous pouvez aussi utiliser `virtualenv` si vous préférez, voire `virtualenvwrapper`):

```shell
python3.9 -m venv ./venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

### Lancement des tests

**Prérequis au lancement des tests**

Une base de données de test et un cache redis sont nécessaires à l'exécution des tests.

* Soit en démarrant les conteneurs de la base de données _pc-postgres-test_ (spécifique aux tests) et du cache
  _redis_ via docker-compose

```shell
    docker-compose -f ../docker-compose-app.yml up -d postgres-test redis
 ```

* Soit en démarrant ces conteneurs via docker

```shell
docker run -d --name postgres -p 5434:5432 \
--env-file ../env_file \
-v postgres_local_data:/var/lib/postgresql/data \
circleci/postgres:12.3-postgis

docker run -d --name redis -p 6379:6379 \
    -v redis_local_data:/data \
    redis redis-server 
```

* Soit en démarrant les services postgresql et redis, par exemple lorsqu'ils ont été installés via _Homebrew_:
  ```shell
  brew services start postgresql
  brew services start redis
  ```

Les tests pourront ensuite être exécutés avec ou sans docker-compose

* Lancement des tests via docker-compose
  ```shell
  pc test-backend # Pour lancer tous les tests
  pc test-backend tests/core/offers/test_api.py::CreateOfferTest::test_create_offer_from_scratch # Pour lancer un test en particulier
  ```

* Lancement des tests depuis la ligne de commande. Il est ainsi très simple d'accéder à `stdin`/`stdout` via le
  paramètre  `-s`, par exemple pour utiliser des breakpoints.
  ```shell
  python -m pytest # Pour lancer tous les tests
  python -m pytest tests/core/offers/test_api.py::CreateOfferTest::test_create_offer_from_scratch # Pour lancer un test en particulier
  ```

### Écriture des tests

Les tests utilisent leur propre base de données. Si un test a besoin d'accéder à la base de données, il faut décorer la
fonction ou la classe avec:

```python
@pytest.mark.usefixtures("db_session")
```

pour encapsuler le test dans une transaction. On peut aussi marquer le module entier en ajoutant sous les imports:

```python
pytestmark = pytest.mark.usefixtures("db_session")
```

Les différentes fixtures utilisées dans les tests sont définies dans `tests/conftest.py`

## Dépendances

- La combinaison `pylint` + `astroid` a parfois quelques soucis : elle est pour l'instant figée à `2.8.3` pour pylint et
  `2.5.6` pour `astroid`. Ceci pourra être modifié quand ces problèmes seront réglés.

## Démarrage du serveur back api

### Option 1 : Lancement via le script `pc` présent dans pass-culture-main

```shell
pc start-backend
```

### Option 2 : Lancement manuel pour pouvoir débugger, se connecter à la DB etc...

Si la base de données n'a pas été initialisée, vous devez suivre les étapes suivantes :

* Ajouter cette variable au fichier `.env.local` à la racine du dépôt (en complétant par le port de votre serveur
  postgresql):

  ```dotenv
  DATABASE_URL=postgresql://pass_culture:passq@localhost:<port>/pass_culture
  ```  

* Installer les extensions et jouer les migrations

  ```shell
  source venv/bin/activate
  flask install_postgres_extensions
  alembic upgrade head
  ```

Vous pouvez maintenant lancer l'application Flask

```shell
python src/pcapi/app.py
```

### Database de jeu

Afin de naviguer/tester différentes situations de données, il existe dans api des scripts permettant d'engendrer des
bases de données "sandbox".

La plus conséquente est `industrial`, elle se créée via la commande:

```bash
flask sandbox -n industrial
```

---

Troubleshooting:

Si la commande sandbox renvoie des erreurs que je n'arrive pas à résoudre, tester de supprimer et reconstruire sa BDD
locale. Pour ça:

- stopper les images lancées
- run: `docker rm -f pc-postgres` <= suppression container
- run: `docker volume rm pass-culture-main_postgres_data` <= suppression données
- relancer: `pc start-backend`
- puis relancer: `pc sandbox -n industrial`

## Authentification Backend pour Flask-Admin

Le backend ne permet pas (encore) de s'authentifier directement, on le fera depuis Webapp ou Pro. Une fois authentifié
depuis l'un de ces deux fronts, un cookie de session est stocké et le back validera le cookie.

## Connexion aux bases de données

Il est possible de se connecter aux bases de données lancées via docker compose en utilisant les informations ci-dessous

- _pc-postgres_
    - user : pass_culture
    - password : passq
    - port : 5434
    - database : pass_culture

- _pc-postgres-test_
    - user : pytest
    - password : pytest
    - port : 5433
    - database : pass_culture

## Linter et hooks

Pour une meilleure expérience de développement sur le repo API, des hooks ([pre-commit](api/hooks/pre-commit)
, [pre-push](api/hooks/pre-push) ) s'exécutent lorsqu'un commit est effectué sur le projet API,

L'environnement python en local est nécessaire pour que les outils d'anlyse de code (`isort`, `batch`, `pylint`...) se
lancent.

Si les hooks ne se lancent pas, lancer `pc install-hooks` (commande incluse dans `pc install`)

## Contributing

Des fichiers `CONTRIBUTING.md` à la racine de différents modules Python du projet apporteront des détails et conseils
spécifiques.

## Troubleshooting

### Installation de psycopg2

> Install openssl with `brew install openssl` if you don't have it already.
>
> add openssl path to `LIBRARY_PATH` :
>
> `export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/`
>
> install psycopg2 with pip `pip3 install psycopg2`


Autre [piste](https://stackoverflow.com/questions/9678408/cant-install-psycopg2-with-pip-in-virtualenv-on-mac-os-x-10-7/62931654#62931654)

## IDE

### PyCharm(IntelliJ)

#### Lancement des tests

Configurer le working directory par défaut pour être toujours à la racine de ce projet
![pycharm-test-config][pycharm-test-configuration]

[pycharm-test-configuration]:./README_resources/pycharm_tests_config.jpg

[pycharm-debugging]:./README_resources/pycharm_debugging.jpg

### Debugging

Pour debugger sous IntelliJ Pycharm, configurer la configuration de lancement python en précisant :

- Le script à lancer : `scr/pcapi/app.py`
- Les variables d'environnement `DATABASE_URL` et `PORT` (Sinon le port sera 5000)
- Le répertoire de lancement (Working directory) qui doit pointer vers api

  ![pycharm-test-config][pycharm-debugging]

#### VS Code

Le fichier de configuration [vscode](api/.vscode/settings.json) permet notamment de lancer `black` et `isort` lorsqu'un
fichier est sauvegardé.

Vérifier que l'interpréteur python utilisé par VSCode est le bon. Taper `cmd+shift+P` puis `Python: select interpreter`
et choisir le python précédemment installé en local (virtual env ou pyenv).
