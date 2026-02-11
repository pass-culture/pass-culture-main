# PASS-CULTURE-API

Voici le backend de l'application pass Culture; il est lancé via `docker compose` en utilisant le fichier
`docker-compose-backend.yml` du répertoire parent de `api`: `pass-culture-main`.

## Installation

### MacOS

Le gestionnaire de paquet recommandé est [Homebrew](https://brew.sh/).

```sh
brew install coreutils libxmlsec1 weasyprint ozeias/postgresql/postgis@15 redis python@3.13 pipx
npm install --global squawk-cli  # yarn peut être utilisé à la place de npm

brew services start redis
brew services start postgresql@15
```

### Linux

L'installation de PostGIS 15 peut demander une configuration en amont :

- pour Ubuntu il faut configurer le repo apt de [postgresql](https://www.postgresql.org/download/linux/ubuntu/)

```sh
sudo apt install python3-dev libpq-dev xmlsec1 libpango-1.0-0 libpangoft2-1.0-0 pipx postgresql-15-postgis-3 pipx
npm install --global squawk-cli  # yarn peut être utilisé à la place de npm

sudo systemctl enable redis
sudo systemctl enable postgresql
```

### Installation commune

#### Natif sans docker

Il faut se positionner dans le dossier `pass-culture-main/api/` et pas à la racine `pass-culture-main/`.

Poetry est le gestionnaire de paquets python, pour ajouter une dépendance il faut mettre à jour le fichier de lock.
L'activation de l'environnement virtuel se fait avec la commande `eval $(poetry env activate)`.

```sh
pipx install poetry
poetry env use python3.13
poetry install --with dev

psql postgres <<EOF
  CREATE ROLE pass_culture SUPERUSER LOGIN PASSWORD 'passq';
  CREATE ROLE pytest SUPERUSER LOGIN PASSWORD 'pytest';
EOF

eval $(poetry env activate)  # activation de l'environnement virtuel
pc setup-no-docker           # créera les tables PostgreSQL et le fichier .env.local.secret
```

> !NOTE  
> Pour passer du setup natif au setup docker, il faut commenter les lignes ajoutées dans le .env.local.secret
> Notamment les champs : `DATABASE_URL`, `DATABASE_URL_TEST` et `FLASK_IP`

##### Lancement de l'application

- Soit via python

```shell
$ eval $(poetry env activate)  # avant chaque commande

# dans des terminaux différents, sans le script pc
$ python src/pcapi/app.py
$ python src/pcapi/backoffice_app.py
$ celery -A pcapi.celery_tasks.celery_worker worker \
  -Q "celery.external_calls.priority,celery.internal_calls.priority,celery.internal_calls.default,celery.external_calls.default" \
  --loglevel=INFO --pool=solo
```

- Soit via les commandes `pc`

Cette façon de faire s'assure de l'existence des composants logiciels (redis, extensions, postgres)) et d'être dans le bon environnement)

```shell
# Lancer l'API
pc start-api-no-docker
# Lancer le Backoffice
pc start-backoffice-no-docker
# Nettoyer les DB, reconstruire la sandbox et jouer les migrations
pc restart-api-no-docker
# Supprimer et recréer les DB (test et data)
pc reset-db-no-docker
# Supprimer et recréer la DB de test
pc reset-db-test-no-docker
```

#### Installation via Docker

- [docker](https://docs.docker.com/install/) (testé avec 19.03.12)
- [docker compose (inclus avec Docker Desktop)](https://docs.docker.com/compose/install/#install-compose) (testé avec 1.26.2)

Pour lancer les serveurs, ces commandes peuvent être utilisées :

- `pc start-backend` pour build l'image docker `pc start-backend --fast` pour ne pas les rebuild et juste les lancer
- Il faut remplacer `start-backend` par `start-proxy-backend` en fonction de la présence d'un proxy sur l'ordinateur
- `pc restart-backend` rebuildera l'image en supprimant les données de la sandbox

Pour peupler la base de données, le script `pc` exécutera `flask` dans l'image docker, par exemple `pc sandbox -n industrial`.

##### Connexion aux bases de données lancées par Docker

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

##### Troubleshooting

Si la commande `pc start-backend` renvoie une erreur de type

```
PermissionError: [Errno 13] Permission denied: '/usr/src/app/src/pcapi/connectors/beneficiaries/educonnect/files/public.cert'
```

Cela peut venir du mode rootless de Docker.
Essayer de [désinstaller le rootless](https://docs.docker.com/engine/security/rootless/troubleshoot/#uninstall) et de faire tourner docker en mode `Defaut`.

### Installer les CLI pour se connecter à l'infrastructure

- [kubectl](https://kubectl.docs.kubernetes.io/installation/kubectl/)
- [gcloud](https://cloud.google.com/sdk/docs/install)

## Database de jeu

Afin de naviguer/tester différentes situations de données, il existe dans api des scripts permettant d'engendrer des
bases de données "sandbox".

La plus conséquente est `industrial`, elle se créée avec cette commande:

```bash
flask sandbox -n industrial  # setup sans docker
pc sandbox -n industrial     # setup avec docker
```

### Troubleshooting

Si la commande sandbox renvoie des erreurs que je n'arrive pas à résoudre, tester de supprimer et reconstruire sa BDD
locale. Pour ça, sans Docker: `pc restart_api_no_docker`

Pour ça, via Docker:

- stopper les images lancées
- run: `docker rm -f pc-postgres` <= suppression container
- run: `docker volume rm pass-culture-main_postgres_data` <= suppression données
- relancer: `pc start-backend`
- puis relancer: `pc sandbox -n industrial`

## Tests

Une fois le le backend lancé, les tests peuvent être exécutés avec ou sans docker compose

### 1. Lancement des tests depuis la ligne de commande dans l'environnement poetry

```shell
pytest -m 'not backoffice' # lance tous les tests hors backoffice
pytest -m 'backoffice' # lance tous les tests du backoffice
pytest tests/core/offers/test_api.py::CreateOfferTest::test_create_offer_from_scratch # Pour lancer un test en particulier
pytest -m backoffice /tests/routes/backoffice/pivots_test.py::GetPivotsPageTest::test_get_pivots_page # Pour lancer un test du backoffice
```

Il est également possible d'accéder à `stdin`/`stdout` via le paramètre `-s`, par exemple pour utiliser des breakpoints.

### 2. Lancement des tests avec docker compose

```shell
pc test-backend # Pour lancer tous les tests backend
pc test-backoffice # pour lancer tous les tests du backoffice
pc test-backend tests/core/offers/test_api.py::CreateOfferTest::test_create_offer_from_scratch # Pour lancer un test en particulier
```

#### Troubleshoot

Si les tests ne se lancent pas avec Docker, il faut recréer la base de données de tests et relancer le cache redis

- Soit en démarrant les conteneurs de la base de données _pc-postgres-test_ (spécifique aux tests) et du cache
  _redis_ via docker compose

```shell
    docker compose -f ../docker-compose-backend.yml up -d postgres-test redis
```

- Soit en démarrant ces conteneurs via docker

```shell
docker run -d --name postgres -p 5434:5432 \
--env-file ../env_file \
-v postgres_local_data:/var/lib/postgresql/data \
postgis/postgis:15-3.4-alpine

docker run -d --name redis -p 6379:6379 \
    -v redis_local_data:/data \
    redis redis-server
```

### 3. Ecriture des tests

Les tests utilisent leur propre base de données. Si un test a besoin d'accéder à la base de données, il faut décorer la
fonction ou la classe avec :

```python
@pytest.mark.usefixtures("db_session")
```

Pour encapsuler le test dans une transaction. On peut aussi marquer le module entier en ajoutant sous les imports :

```python
pytestmark = pytest.mark.usefixtures("db_session")
```

Les différentes fixtures utilisées dans les tests sont définies dans `tests/conftest.py`

## Ajout de données avec les factories

- Lancer python avec docker: `pc python`, sans docker: `flask shell`
- Dans l'éditeur de code, identifier la factory `pcapi.core`.
  Tous les arguments sont renseignés par défaut et peuvent être surchargés.
- importer la factory et l'utiliser : les données sont disponibles en localhost

### exemple 1 - créer un utilisateur

```
>>> from pcapi.core.users.factories import UserFactory;
>>> UserFactory(email='user@example.com’);
```

On peut ensuite se connecter avec ce mail et le mot de passe par défaut en localhost.

### exemple 2 - création d'un utilisateur et d'une structure liée

```
>>> from pcapi.core.users.factories import UserFactory;
>>> user = UserFactory(email='marie2@app.com’)
>>> from pcapi.core.offerers.factories import OffererFactory
>>> factory = OffererFactory(siren=444444444)
>>> from pcapi.core.offerers.factories import UserOffererFactory
>>> UserOffererFactory(user, offerer)
```

On peut aussi surcharger directement les arguments des factories appelées par d'autres factories, en préfixant l'argument avec le nom de la factory secondaire suivie d'un double underscore. Les deux lignes suivantes sont équivalentes à celles qui précèdent:

```
>>> from pcapi.core.offerers.factories import UserOffererFactory
>>> UserOffererFactory(user__email='marie2@app.com’, offerer__siren=444444444)
```

### en cas d’erreur, rollback avant de recommencer la transaction

```
>>> from pcapi.models import db
>>> db.session.rollback()
```

## Secrets et variables d'environnement

Les variables d'environnement nécessaires au bon fonctionnement mais qui portent des données sensibles (identifiants, clés d'API, ...)
ne sont pas enregistrés dans les fichiers d'environnement du dépôt.
Il faut les ajouter dans le fichier `api/.env.local.secret` .

## Scan du repo par GitGuardian

Une Github Action est lancée à chaque push sur le repo, lançant un scan de fuites de secrets GitGuardian.
Pour ignorer un faux positif, il convient d'ajouter un commentaire _inline_ dans le code: `# ggignore`
cf <https://github.com/GitGuardian/ggshield#in-code>

## Linter et hooks

Pour une meilleure expérience de développement sur le repo API, des hooks ([pre-commit](api/hooks/pre-commit)
, [pre-push](api/hooks/pre-push) ) s'exécutent lorsqu'un commit est effectué sur le projet API,

L'environnement python en local est nécessaire pour que les outils d'analyse de code (`mypy` & `ruff`) se lancent.

Si les hooks ne se lancent pas, lancer `pc install-hooks` (commande incluse dans `pc install`)

## Ecriture d'une tâche automatique (cron)

Les commandes à lancer régulièrement (par example des synchronisations journalières) sont définies dans les fichiers `src/pcapi/*/commands.py`
Pour que les commandes soient enregistrées par Flask, il faut que le fichier `path/to/commands.py` soit référencé dans la fonction `install_commands` de `api/src/pcapi/scripts/install.py`

Pour que les commandes soient exécutées, il faut ouvrir une PR sur le repo pass-culture/pass-culture-deployment
Les infos sont dans le [README](https://github.com/pass-culture/pass-culture-deployment)

## IDE

### PyCharm(IntelliJ)

#### Lancement des tests

Configurer le working directory par défaut pour être toujours à la racine de ce projet
![pycharm-test-config][pycharm-test-configuration]

[pycharm-test-configuration]: ./README_resources/pycharm_tests_config.jpg
[pycharm-debugging]: ./README_resources/pycharm_debugging.jpg

#### Debugging

Pour debugger sous IntelliJ Pycharm, configurer la configuration de lancement python en précisant :

- Le script à lancer : `scr/pcapi/app.py`
- Les variables d'environnement `DATABASE_URL` et `PORT` (Sinon le port sera 5001)
- Le répertoire de lancement (Working directory) qui doit pointer vers api

  ![pycharm-test-config][pycharm-debugging]

### VS Code

Le fichier de configuration [vscode](api/.vscode/settings.json) permet notamment de lancer `black` et `isort` lorsqu'un
fichier est sauvegardé.

Vérifier que l'interpréteur python utilisé par VSCode est le bon. Taper `cmd+shift+P` puis `Python: select interpreter`
et choisir le python précédemment installé en local (virtual env ou pyenv).

#### Exécution des tests

Il est possible de lancer / débugger les tests python directement depuis VSCode. Pour cela il faut avoir installé les extensions `ms-python.python` et `ms-python.debugpy`.

On peut voir la liste des tests dans l'onglet Testing, où l'on peut lancer les tests par fonction / classe / fichier / dossier. Lorsqu'on est dans un fichier de test, on peut également utiliser les icones placées directement à côté de chaque fonction.

Quelques commandes VSCode utiles lorsqu'on est dans un fichier de test, avec leur équivalent `Debug Test` :

- `Test: Run Test in Current File`
- `Test: Run Test at Cursor`
- `Test: Rerun Last Run`
- `Test: Rerun Failed Tests`

Voir <https://code.visualstudio.com/docs/python/testing> pour plus d'informations.

## Contributing

Des fichiers `CONTRIBUTING.md` à la racine de différents modules Python du projet apporteront des détails et conseils
spécifiques.

## OpenAPI

Une documentation Swagger des APIs est générée selon l'OpenAPI Specification (OAS3) grâce à un schéma généré par
Spectree :

- [App Native](https://backend.passculture.app/native/swagger)
- [Adage](https://backend.passculture.app/adage-iframe/swagger)
- [API webhooks et cloud tasks](https://backend.passculture.app/apidoc/swagger)
- [API pro privée](https://backend.passculture.app/pro/swagger)
- [API publique](https://developers.passculture.pro/rest-api)

## Liens des mocks API

- [Mock API billeterie](https://mock-api-billeterie.ehp.passculture.team/)

## Troubleshooting

### Installation de psycopg2

Installer `openssl` avec `brew install openssl`.

Ajouter `openssl` au path `LIBRARY_PATH` (path for intel chip brew) `export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/`.

Sur mac, vous pouvez aussi avoir besoin de lancer `brew install postgresql`.

Autre [piste](https://stackoverflow.com/questions/9678408/cant-install-psycopg2-with-pip-in-virtualenv-on-mac-os-x-10-7/62931654#62931654).

### Tests qui échouent

#### Problème de cache

Après avoir lancé les tests avec Docker (`pc test-backend`), les tests peuvent échouer en les lançant avec Python (`python -m pytest`)

Il faut supprimer les fichiers de cache de pré-compilation de Python, par exemple avec la commande suivante

```sh
find . -type f -name "*.py[co]" -delete -or -type d -name "__pycache__" -delete
```

### Nettoyage des images docker

Lors d'un changement dans le fichier `requirements.py`, une nouvelle image docker de l'api est générée. Il convient de régulièrement supprimer les images "dangling" pour ne pas qu'elles prennent trop de place sur le disque local. (cf [doc docker](https://docs.docker.com/config/pruning/#prune-images)).

```
docker image prune
```
