# pass-culture-api

[![Coverage Status](https://coveralls.io/repos/github/pass-culture/pass-culture-api/badge.svg)](https://coveralls.io/github/pass-culture/pass-culture-api)

C'est le backend de l'application Pass Culture.

Dans le cadre du projet pass-culure, l'api pass culture est lançée via docker-compose et en utilisant le fichier `docker-compose-app.yml` du répertoire parent de api, soit `pass-culture-main`.

Plus de détails sur le lancement de l'infra docker-compose sont accessibles dans le README dans https://github.com/pass-culture/pass-culture-main.

## Swagger
L'api pass culture dispose d'un swagger accessible via ce lien : [http://localhost:/apidoc/swagger](http://localhost/apidoc/swagger) <br>
C'est une api générée et fonctionnelle.<br>
Elle ne contient toutefois pas les endpoints de l'api publique.

Il existe une ancienne api très incomplète et non utilisable (A décommissioner) [http://localhost/api/doc](http://localhost/api/doc)

## Installation et Tests

- ### Installation des requirements
  - Avec venv (ou virtualenv si vous préférez)
    ```shell
    python3.9 -m venv ./venv
    source venv/bin/activate 
    pip install -e .
    pip install -r requirements.txt
    ```
  
- ### Lancement des tests
  - Prérequis aux lancement des tests
    - Lancement de la base de donnée pc-postgres-test (spécifique aux tests) et du cache redis via docker-compose
      ```shell
      docker-compose -f ../docker-compose-app.yml up -d postgres-test redis
      ```
    
  - Lancement des tests depuis la ligne de commande
    ```shell
    python -m pytest # Pour lancer tous les tests
    python -m pytest tests/scripts/offerer/generate_and_save_api_key_for_offerer_test.py # Pour lancer un test en particulier
    ```
  
  - Lancement des tests depuis PyCharm(IntelliJ)
    
    Configurer le working directory par défaut pour être toujours à la racine de ce projet
    ![pycharm-test-config][pycharm-test-configuration]

- ### Écriture des tests
  - Les tests utilisent leur propre base de données
   Si un test a besoin d'accéder à la base de donnée, il faut le décorer avec `@pytest.mark.usefixtures("db_session")` pour encapsuler le test dans une transation et éviter des colisions entre différents tests

   les différentes fixtures utilisées dans les tests sont définies dans `tests/conftest.py`

## Dépendances

- La combinaison pylint-astroid a parfois quelques soucis : elle est pour
l'instant figée à 2.8.3 pour pylint et 2.5.6 pour astroid. Ceci pourra être
modifié quand ces problèmes seront réglés côté pylint/astroid.

## Démarrage du serveur back api
- Option 1 : Lancement du serveur back api depuis le script pc présent dans le dossier parent
  https://github.com/pass-culture/pass-culture-main
  
- Option 2 : Procédure de lancement en local pour pouvoir débugger via son ide préféré, se connecter à la DB etc... 
  - Un fichier docker compose complet est fourni dans le dossier parent et il est conseillé de l'utiliser car il est maintenu à jour.
  - Lancement de la base de donnée pc-postgres et du cache redis via docker-compose
      ```shell
      docker-compose -f ../docker-compose-app.yml up -d postgres redis
      ```
  - A titre informatif, si toutefois vous vouliez lançer la DB et le redis vous même, vous pourriez aussi faire (équivalement du docker compose)
      ```shell
      docker run -d --name postgres -p 5434:5432 \
          --env-file ../env_file \
          -v postgres_local_data:/var/lib/postgresql/data \
          circleci/postgres:12.3-postgis
    
      docker run -d --name redis -p 6379:6379 \
          -v redis_local_data:/data \
          scalingo/redis redis-server 
      ```
  - Jouer les migrations DB
    <br>Si la base de donnée n'a pas été initialisée (En d'autre terme si vous n'avez jamais fait par exemple de docker-compose -f ../docker-compose-app.yml up )
    alors vous devez suivre les étapes suivantes pour l'initialisation 
    -  Créer une variable d'environnement pour SQLAlchemy
    ```shell
    export DATABASE_URL=postgresql://pass_culture:passq@localhost:5434/pass_culture
    ```  
    ```shell
      source venv/bin/activate # Au cas ou vous l'auriez oublié :P
      python src/pcapi/install_database_extensions.py
      alembic upgrade head
      ```
    - Injecter les données de tests (sandbox)
    ```shell
    python -m nltk.downloader punkt stopwords   # Cette ligne c'est pour downloader les médiations (images thumbnail des offres) 
    python src/pcapi/scripts/pc.py sandbox -n industrial
    ```
    - Lancer l'appli
    ```shell
    PORT=80 python src/pcapi/app.py
    ```
  
## Authentification Back Api
L'api back ne permet pas de s'authentifier directement.
Il est possible de s'authentifier depis l'un des deux fronts :
- Webapp
- Pro

Une fois authentifié depuis l'un des deux fronts, un cookie de session est stocké et le back reconnait le cookie.

## Connexions au bases de données (DB NAVIGATOR par exemple)
Il est possible de se connecter aux bases de données lançées via docker compose en utiilisant les informations ci-dessous
- pc-postgres
  - user : pass_culture
  - password : passq 
  - port : 5434
  - database : pass_culture
    
- pc-postgres-test
  - user : pytest
  - password : pytest 
  - port : 5433
  - database : pass_culture
  
## Debugging
Pour Debugger sous IntelliJ Pycharm, configurer la configuration de lancement python en précisant :
  - Le script à lancer : scr/pcapi/app.py
  - Les variable d'environnement DATABASE_URL et PORT (Sinon le port sera 5000)  
  - Le répertoire de lancement (Working directory) qui doit pointer vers api
    
    ![pycharm-test-config][pycharm-debugging]
    

## Linter et hooks
Black et ISort permettent le reformattage du code et des imports.
Ils sont lançés automatiquement à chaque commit une fois les hooks de gitlab configurés en local.
Pour les configurer vous pouvez utiliser le script pc :
```bash
cd .. # Se placer sur le dossier pass-culture-main
./pc install-hooks # le script pc va créer les liens vers pre-push et pre-commit dans le .git/modules/api/hooks 
```

## Problèmes rencontrés

- Erreur durant le pip install -r requirements 
```
Install openssl with brew install openssl if you don't have it already.
add openssl path to LIBRARY_PATH :
export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/
install psycopg2 with pip pip3 install psycopg2
```

- if you got errors, during requirements installation, about `psycopg`, this may help you
  - https://stackoverflow.com/questions/9678408/cant-install-psycopg2-with-pip-in-virtualenv-on-mac-os-x-10-7/62931654#62931654

  
[pycharm-test-configuration]:./README_resources/pycharm_tests_config.jpg
[pycharm-debugging]:./README_resources/pycharm_debugging.jpg
