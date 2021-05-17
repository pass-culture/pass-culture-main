# pass-culture-api

[![Coverage Status](https://coveralls.io/repos/github/betagouv/pass-culture-api/badge.svg)](https://coveralls.io/github/betagouv/pass-culture-api)

C'est le backend de l'application Pass Culture.

Dans le cadre du projet pass-culure, l'api pass culture est lançée via docker-compose et en utilisant le fichier `docker-compose-app.yml` du répertoire parent de api, soit `pass-culture-main`.

Plus de détails sur le lancement de l'infra docker-compose sont accessibles dans le README dans https://github.com/betagouv/pass-culture-main.

## Swagger
L'api pass culture dispose d'un swagger accessible via ce lien : [http://localhost:80/api/doc](http://localhost:80/api/doc)
 
Chantier en cours ...

/api/doc --> ni généré ni maintenu

https://backend.passculture.beta.gouv.fr/apidoc/swagger --> Généré et fonctionnel mais ne contient pas pour le moment l'api publique

Idée c'est de le fusionner avec les autres groupes swagger générés qui fonctionnent

## Installation et Lancement des tests

- ### Installation des requirements
  - Avec venv (ou virtualenv si vous préférez)
    ```bash
    python3.9 -m venv ./venv
    source venv/bin/activate 
    pip install -e .
    pip install -r requirements.txt
    ```
  
- ### Lancement des tests
  - Prérequis aux lancement des tests
    - Lancement de la base de donnée postgres-postgis et du cache redis
      ```bash
        docker-compose -f ../docker-compose-app.yml up -d postgres-test redis
      ```
    
  - Lancement des tests depuis la ligne de commande
    ```bash
    python -m pytest
    ```
  
  - Lancement des tests depuis PyCharm(IntelliJ)
    
    Configurer le working directory par défaut pour être toujours à la racine de ce projet
    ![pycharm-test-config][pycharm-test-configuration]
    

## Démarrage du serveur back api
- Option 1 : Lancement du serveur back api depuis le script pc présent dans le dossier parent
  https://github.com/betagouv/pass-culture-main

## Authentification Back Api
L'api back ne permet pas de s'authentifier directement.
Il est possible de s'authentifier depis l'un des deux fronts :
- Webapp
- Pro

Une fois authentifié depuis l'un des deux fronts, un cookie de session est stocké et le back reconnait le cookie.

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
