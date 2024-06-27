# PASS-CULTURE-API

Voici le backend de l'application pass Culture; il est lancé via `docker-compose` en utilisant le fichier
`docker-compose-backend.yml` du répertoire parent de `api`: `pass-culture-main`.

Plus de détails sur le lancement de l'infra docker-compose sont accessibles dans le
[README de pass-culture-main](https://github.com/pass-culture/pass-culture-main#readme)

## I. OpenAPI

Une documentation Swagger des APIs est générée selon l'OpenAPI Specification (OAS3) grâce à un schéma généré par
Spectree :

* [API Contremarque](https://backend.passculture.app/v2/swagger)
* [App Native](https://backend.passculture.app/native/swagger)
* [Adage](https://backend.passculture.app/adage-iframe/swagger)
* [API privée et API publique dépréciée](https://backend.passculture.app/apidoc/swagger)
* [API pro publique v2](https://backend.passculture.app/v2/swagger)
* [API pro privée](https://backend.passculture.app/pro/swagger)
* [API publique d'offres individuelles](https://backend.passculture.app/public/offers/v1/swagger)

## II. Liens des mocks API
* [API "Charlie" billeterie](https://mock-api-billeterie.ehp.passculture.team/)

## III. Démarrage du serveur back api

### III.1 Pré-requis

On utilise Poetry pour gérer nos dépendances. Par défaut, Poetry crée l'environnement virtuel dans un dossier
qui dépend du système d'exploitation.

La méthode d'activation de l'environnement virtuel recommandée est l'utilisation de la commande `poetry shell`.

Pour un usage avancé comme avoir plusieurs environnements virtuels, il existe [d'autres manières d'activer son
environnement virtuel](https://python-poetry.org/docs/basic-usage#activating-the-virtual-environment).

Une gestion plus fine de l'environnement virtuel utilisé par `poetry` peut être trouvée sur ce lien : [Managing environments | Documentation | Poetry](https://python-poetry.org/docs/managing-environments/)

*NOTE* : Poetry n'est pas utilisé dans les conteneurs Docker, i.e. la commande `flask` est directement accessible.
*NOTE* : L'ajout de dépendance doit se faire par Poetry pour mettre à jour le fichier lock.

Avec `poetry` et Python **3.11** :

```shell
curl -sSL https://install.python-poetry.org | python3 -
poetry env use python3.11
poetry install --with dev
```

La bonne version de python est à installer soit à travers le gestionnaire de paquet du système d'exploitation,
soit en utilisant `pyenv`.

La génération de PDF via `weasyprint` nécessite également de suivre
ces [étapes](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) d'installation.

Le lint des migrations, effectué lors du [hook de precommit](../.githooks/pre-commit), nécessite [Squawk — a linter for Postgres migrations](https://squawkhq.com/).

``` shell
npm install --global squawk-cli
```

### III.2 Lancement de l'api

Il y a deux options pour lancer l'application Flask.
La première consiste en l'utilisation d'un utilitaire dédié (`pc`) qui utilise docker-compose. Cette méthode permet d'avoir le plus simplement un server HTTP.

La seconde méthode consiste à créer en local les différents constituant logiciel afin d'avoir une maitrise plus fine des traitements et un temps de setup plus court.
 
#### III.2.1 Option 1 : Lancement via le script `pc` présent dans pass-culture-main

```shell
#Start api and backoffice
pc start-backend
#Restart after removing the database and file
pc restart-backend
```
#### III.2.2 Option 2 : Lancement manuel

Les dépendances suivantes doivent également être installées: 
- Postgresql
- PostGis
- Redis


#### III.2.2.a Postgresql
Les informations générales sur les étapes d'installation sont disponibles sur le lien https://www.postgresql.org/download/
  - Linux : 
    * Ubuntu : 
     Il est préférable de cibler la version utilisée en production. Celle-ci peut se retrouver dans le fichier doker-compose-backend.
     A la date de rédaction postgresql 15.0 est utilisé. 
     Configuration du repos apt
     ```shell
     sudo apt install -y postgresql-common
     sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

     ```
     install version 15
     ```shell
    # Update the package lists:
    sudo apt update

    # Install the latest version of PostgreSQL:
    # If you want a specific version, use 'postgresql-16' or similar instead of 'postgresql'
    sudo apt -y install postgresql-15
    ```
     `apt install postgis` pour Ubuntu ou `pacman -S postgis` pour Arch Linux
  
  - Macos :

    Installer postgres.app depuis ce lien [Postgres.app](https://postgresapp.com/), choisir la version iso à la prod (à date postgresql 15)
Il est nécessaire de configurer des accès utilisateur afin de lancer les scripts.
* Pour les utilisateur Linux/Mac:
<br> Il faut créer un role au même nom que l'utilisateur:
  ```shell
  $ psql -U postgres
  > CREATE ROLE <myuser> LOGIN password 'secret';
  > CREATE DATABASE <myuser> ENCODING 'UTF8' OWNER <myuser>;
  ```


#### III.2.2.b PostGIS

- Verifier que `PostGIS` est bien installé. Si ce n'est pas le cas: 
  <br>pour installer `PostGIS` dans les systèmes d'exploitation qui ne le fournissent pas avec `PostgreSQL`:

  - Ubuntu:
    * Configurer le repo apt de postgresql( conf chapitre précédent)
    * installer postgis-15
   ```
    sudo apt install postgresql-15-postgis-3
   ```
  - Windows : après l'installation de `PostgreSQL`, [Stackbuilder](https://www.bostongis.com/PrinterFriendly.aspx?content_name=postgis_tut01)
    permet d'installer `PostGIS`
  - MacOS : `PostGIS` est fourni avec la distribution [Postgres.app](https://postgresapp.com/). Si une autre manière
    d'installer `PostgreSQL` a été choisie, alors la commande d'installation est `brew install postgis`.

#### III.2.2.c Redis
Le lien officiel pour l'installation: https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/

### III.2.2.d Initialisation de l'application
Pour initialiser l'application, vous devez suivre les étapes suivantes :

* Soit en lançant la commande suivante qui va créer les bases de données pour l'api et pour les tests, installer les extensions postgres et jouer les migrations. Il est nécessaire de rendre l'utilisateur qui execute cette ligne de commande soit `sudoer`


  ```shell
  pc setup-no-docker
  ```

* Soit en réalisant les étapes suivantes une par une:
  - créer les _users_ suivants:
  <br>il faut pour cela changer d'utilisateur afin de se connecter au server postgresql.
  <br> A l'installation un utilisateur système est créé et doit être utilisé pour se connecter à la base de données.
    ```shell 
    >sudo su postgres
    >psql
    ```
    il faut ensuite créer les utilisateurs:

    ```sql
    CREATE ROLE pass_culture SUPERUSER LOGIN PASSWORD 'passq';
    CREATE ROLE pytest SUPERUSER LOGIN PASSWORD 'pytest';
    FLASK_BACKOFFICE_PORT=5002
    ```
  - créer les _databases_ associés (cf. les commandes `recreate_database` `recreate_database_test` dans le fichier `start_backend_no_docker`)

  - Ajouter ces variables au fichier `.env.local.secret` à la racine du dossier `api/` (en complétant par le port de
    votre serveur postgresql, habituellement `5432`):

    ```dotenv
    DATABASE_URL=postgresql://pass_culture:passq@localhost:<port>/pass_culture
    DATABASE_URL_TEST=postgresql://pytest:pytest@localhost:<port>/pass_culture_test
    "FLASK_BACKOFFICE_PORT=5002"
    ```

  - Installer les extensions et jouer les migrations en ayant dans le `poetry shell` :

    ```shell
    flask install_postgres_extensions
    alembic upgrade pre@head
    alembic upgrade post@head
    ```
### III.2.2.e Lancement de l'application
Vous pouvez maintenant lancer l'application back
 - Par le script python
   * pour l'API
    ```shell
    python src/pcapi/app.py
    ```
    * pour le Backoffice
    ```shell
    python src/pcapi/backofficeapp.py
    ```
 - Par pc 
  <br>Cette methode relance les migrations et s'assure de l'existence des composants logiciels (redis, extension postgres)
  ```
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

Si vous souhaitez (ré)utiliser docker par la suite, n'oubliez pas de commenter `DATABASE_URL`, `DATABASE_URL_TEST`et `FLASK_BACKOFFICE_PORT` dans `.env.local.secret`, et d'arrêter le service redis-server


## IV. Tests
**Prérequis au lancement des tests**

Une base de données de test et un cache redis sont nécessaires à l'exécution des tests. 
### IV.1 Test avec Docker

Pour lancer les tests il faut d'abord lancer l'api
  ```
  pc start-backend
  ```
Et lancer les tests 
  ```shell
  pc test-backend # Pour lancer tous les tests backend
  pc test-backoffice # pour lancer tous les tests du backoffice
  pc test-backend tests/core/offers/test_api.py::CreateOfferTest::test_create_offer_from_scratch # Pour lancer un test en particulier

  ```

### IV.2 Test dans l'environnement poetry
Suite à l'initialisation de l'application il existe déjà un serveur redis et une base de données test.
<br>Il suffit alors de :
* Lancer les tests depuis la ligne de commande dans un `poetry shell`. Il est ainsi très simple d'accéder à
  `stdin`/`stdout` via le paramètre  `-s`, par exemple pour utiliser des breakpoints.
  ```shell
  pytest # Pour lancer tous les tests
  pytest tests/core/offers/test_api.py::CreateOfferTest::test_create_offer_from_scratch # Pour lancer un test en particulier
  ```
Il est également possible d'utiliser le serveur redis et la base de données test conteneurisée depuis le shell flask

* Soit en démarrant les conteneurs de la base de données _pc-postgres-test_ (spécifique aux tests) et du cache
  _redis_ via docker-compose

  ```shell
    docker-compose -f ../docker-compose-backend.yml up -d postgres-test redis
  ```
* Soit en démarrant ces conteneurs via docker

  ```shell
  docker run -d --name postgres -p 5434:5432 \
  --env-file ../env_file \
  -v postgres_local_data:/var/lib/postgresql/data \
  postgis/postgis:15-3.4-alpine

  docker run -d --name redis -p 6379:6379 \
      -v redis_local_data:/data \
      redis redis-server
    ```
Il suffit alors d'éxecuter les tests comme présenté précédemment.
### IV.3. Écriture des tests

Les tests utilisent leur propre base de données. Si un test a besoin d'accéder à la base de données, il faut décorer la
fonction ou la classe avec :

```python
@pytest.mark.usefixtures("db_session")
```

pour encapsuler le test dans une transaction. On peut aussi marquer le module entier en ajoutant sous les imports :

```python
pytestmark = pytest.mark.usefixtures("db_session")
```

Les différentes fixtures utilisées dans les tests sont définies dans `tests/conftest.py`


## V. Secrets et variables d'environnement

Les variables d'environnement nécessaires au bon fonctionnement mais qui porte des données sensibles (identifiants, clés d'API, ...)
ne sont pas enregistrés dans les fichiers d'environnement du dépôt.
Il faut les ajouter dans le fichier `api/.env.local.secret` .

## VI. Scan du repo par GitGuardian

Une Github Action est lancée à chaque push sur le repo, lançant un scan de fuites de secrets GitGuardian.
Pour ignorer un faux positif, il convient d'ajouter un commentaire _inline_ dans le code: `# ggignore`
cf https://github.com/GitGuardian/ggshield#in-code


## Database de jeu

Afin de naviguer/tester différentes situations de données, il existe dans api des scripts permettant d'engendrer des
bases de données "sandbox".

La plus conséquente est `industrial`, elle se créée depuis un `poetry shell` via la commande:

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

Le backend ne permet pas (encore) de s'authentifier directement.
On peut s'authentifier de deux manières:
- En se connectant sur Pro. Une fois authentifié, un cookie de session est stocké et le back validera le cookie.
- Sans session depuis le front **Pro**, une authentification est proposée via Google Account. Seuls les utilisateurs du projet **passculture.app** sont autorisés.

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

## Ajout de données avec les factories

- Lancer python avec docker: `pc python`
- Dans l'éditeur de code, identifier la factory `pcapi.core`.
  Tous les arguments sont renseignés par défaut et peuvent être surchargés.
- importer la factory et l'utiliser: les données sont disponibles en localhost

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

## Linter et hooks

Pour une meilleure expérience de développement sur le repo API, des hooks ([pre-commit](api/hooks/pre-commit)
, [pre-push](api/hooks/pre-push) ) s'exécutent lorsqu'un commit est effectué sur le projet API,

L'environnement python en local est nécessaire pour que les outils d'analyse de code (`isort`, `batch`, `pylint`...) se
lancent.

Si les hooks ne se lancent pas, lancer `pc install-hooks` (commande incluse dans `pc install`)

## Contributing

Des fichiers `CONTRIBUTING.md` à la racine de différents modules Python du projet apporteront des détails et conseils
spécifiques.

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

#### Problème de DeprecationWarning 

En lançant les tests avec `python -m pytest`, si les tests échouent avec ce message `E   DeprecationWarning: 'cgi' is deprecated and slated for removal in Python 3.13` , il faut les relancer en ajoutant le flag suivant à la commande : `-W ignore::DeprecationWarning` (ou éventuellement ajouter un alias au terminal)

### Nettoyage des images docker

Lors d'un changement dans le fichier `requirements.py`, une nouvelle image docker de l'api est générée. Il convient de régulièrement supprimer les images "dangling" pour ne pas qu'elles prennent trop de place sur le disque local. (cf [doc docker](https://docs.docker.com/config/pruning/#prune-images)).

```
docker image prune
```

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
- Les variables d'environnement `DATABASE_URL` et `PORT` (Sinon le port sera 5001)
- Le répertoire de lancement (Working directory) qui doit pointer vers api

  ![pycharm-test-config][pycharm-debugging]

#### VS Code

Le fichier de configuration [vscode](api/.vscode/settings.json) permet notamment de lancer `black` et `isort` lorsqu'un
fichier est sauvegardé.

Vérifier que l'interpréteur python utilisé par VSCode est le bon. Taper `cmd+shift+P` puis `Python: select interpreter`
et choisir le python précédemment installé en local (virtual env ou pyenv).

## Ecriture d'une tâche automatique (cron)

Les commandes à lancer régulièrement (par example des synchro journalières) sont définies dans les fichiers `src/pcapi/*/commands.py`
Pour que les commandes soient enregistrées par Flask, il faut que le fichier `path/to/commands.py` soit référencé dans la fonction `install_commands` de `api/src/pcapi/scripts/install.py`

Pour que les commandes soient exécutées, il faut ouvrir une PR sur le repo pass-culture/pass-culture-deployment
Les infos sont dans le [README](https://github.com/pass-culture/pass-culture-deployment)
