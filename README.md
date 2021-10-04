# pass-culture-main

Le repo `main` contient 6 sub modules du pass Culture suivants :

- l'[api](https://github.com/pass-culture/pass-culture-api) (Flask)
- le portail [pro](https://github.com/pass-culture/pass-culture-pro) (React), pour les acteurs culturels
- la [webapp](https://github.com/pass-culture/pass-culture-browser) (React) : version web de l'application des jeunes, remplacée progressivement par l'[app native](https://github.com/pass-culture/pass-culture-app-native/)
- [adage-front](https://github.com/pass-culture/pass-culture-adage-front) (React), application frontend pour les rédacteurs de projets scolaires
- [doc](https://github.com/pass-culture/pass-culture-doc) : documentation de l'API pour les partenaires du pass Culture
- [maintenance-api](https://github.com/pass-culture/pc-maintenance) : page de maintenance

## Installation

#### Installer les bibliothèques

- Docker
  - [docker](https://docs.docker.com/install/) (testé avec 19.03.12)
  - [docker-compose](https://docs.docker.com/compose/install/#install-compose) (testé avec 1.26.2)
- [NVM](https://github.com/creationix/nvm) (Node Version Manager)
  - `curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash`
- [Node](https://nodejs.org/en/download/)
  - `nvm install` dans un répertoire front
- [Yarn](https://yarnpkg.com/lang/fr/docs/install/)
  - Install [HomeBrew](https://brew.sh/index_fr) (MacOS)
  - `brew install yarn --ignore-dependencies` (MacOS)
  - `sudo` (Linux)
- GPG (outil de (dé)chiffrement)
  - [GPG Suite](https://gpgtools.org/) (MacOS)
  - `sudo apt install gpg` (Linux)

#### Pour MacOS spécifiquement

- CoreUtils
  - `brew install coreutils`

#### Installer les CLI

- Netlify
  - `npm install -g netlify-cli@1.2.3`

**Il vous faudra une clé SSH sur votre profil GitHub pour pouvoir cloner le repository.**

#### Installer l'ensemble des projets

1. `git clone git@github.com:pass-culture/pass-culture-main.git pass-culture-main`
2. `cd pass-culture-main`
3. `git submodule update --init --recursive`
4. `./pc symlink`
5. `pc install`

### Lancer les applications

#### L'api

- `pc start-backend`
- Tester `http://localhost/apidoc/swagger#/default` et vous devriez accéder au swagger
- Aller sur l'url `http://localhost/pc/back-office/` pour accéder au back office Flask Admin
- `pc sandbox -n industrial` (pour peupler la BDD)

#### La webapp

- `pc start-webapp`
- `http://localhost:3000/` devrait être lancé et fonctionnel

- Connectez-vous avec `pctest.jeune93.has-booked-some.v1@example.com` et `user@AZERTY123`

#### Le portail pro

- `pc start-pro`
- `http://localhost:3001/` devrait être lancé et fonctionnel
- Connectez-vous avec `pctest.admin93.0@example.com` et `user@AZERTY123`

#### Adage-front

- `pc start-adage-front`
- `http://localhost:3002/` devrait être lancé et fonctionnel
- Connectez-vous avec un token valide en le passant en query param (pour générer un token valide, générez le via le helper de test dans l'API)

#### Flask Admin

- lancer l'`api`
- lancer `pro` ou `webapp`
- se connecter avec les identifiants d'un compte admin
- visiter `http://localhost/pc/back-office/`

### Exécution des tests (API, WebApp, Pro, adage-front)

- API
  1. `pc start-backend`
  2. `pc test-backend` (permet de lancer tous les tests de l'API)
  3. `pc test-backend <path_to_test_file> -k <test_name>` (permet de lancer des tests spécifiques)
  4. `pc test-backend <path_to_test_file> -x <test_name>` (permet de lancer des tests spécifiques et d'arrêter l'exécution au premier test fail)
- WEBAPP / PRO / ADAGE-FRONT
  1. `yarn test:unit`
  2. `yarn test:cafe` (tests end2end)
  - le backend (`api`) doit être lancé
  - il doit y avoir des données dans la sandbox au préalable `pc sandbox -n testcafe`

## Développement

### Environnement python local

- Installer Python 3.9 et `pip`
- Monter un [virtualenv](https://python-guide-pt-br.readthedocs.io/fr/latest/dev/virtualenvs.html) afin d'avoir un environnement isolé et contextualisé pour les besoins de l'API

  1. `pip install virtualenv`
  2. `cd pass-culture-main/api`
  3. `python -m venv venv`
  4. `source venv/bin/activate`
  5. `pip install -r requirements.txt`

Il est utile de lancer périodiquement un `pip install -r requirements.txt` pour mettre à jour les dépendances (chose faite automatiquement par le docker lorsqu'il se lance).

**Hooks de commit**

Lorsqu'un commit est effectué sur le projet API, les hooks de commits ([pre-commit](api/hooks/pre-commit), [pre-push](api/hooks/pre-push) ) se lancent.

L'environnement python en local est nécessaire pour que les outils d'anlyse de code (`isort`, `batch`, `pylint`...) se lancent.

Si les hooks ne se lancent pas, lancer `pc install-hooks` (commande incluse dans `pc install`)

**_Troubleshooting_**

En cas d'erreur lors de l'installation des dépendances avec psycopg, [ceci peut vous aider](https://stackoverflow.com/questions/9678408/cant-install-psycopg2-with-pip-in-virtualenv-on-mac-os-x-10-7/62931654#62931654).

- `pip install -e .`

### Editeur de code (IDE)

Point de contrôle (API) :
Pour une meilleure expérience de développement sur le repo API, vérifier que les fichiers sont correctement formattés (avec `black` et `isort`) lorsqu'un fichier est sauvegardé.

**VS Code**

Le fichier de configuration [vscode](api/.vscode/settings.json) permet notamment de lancer `black` et `isort` lorsqu'un fichier est sauvegardé.

Vérifier que l'interpreteur python utilisé par VSCode est le bon. Taper `cmd+shift+P` puis `Python: select interpreter` et choisir le python précédemment installé en local (virtual env ou pyenv).

### Migration

Pour effectuer une migration du schéma de la base de données, il est recommandé d'effectuer les étapes suivantes :

1. Modifier le modèle applicatif dans les fichiers python
2. Générer la migration de manière automatique

```
pc alembic  revision --autogenerate -m nom_de_la_migration
```

3. Enlever les commentaires "please adjust" générés par alembic dans le fichier de migration

4. Jouer la migration : `pc alembic upgrade head`

Autres commandes utiles :

- Revenir 1 migration en arrière : `pc alembic downgrade -1`
- Afficher le sql généré entre 2 migrations sans la jouer : `pc alembic upgrade e7b46b06f6dd:head --sql`

### Test

Pour tester le backend:

```bash
pc test-backend
```

Pour tester la navigation du site web

```bash
pc -e production test-cafe-webapp -b firefox
```

Exemple d'une commande test en dev sur chrome pour un fichier test particulier:

```bash
pc test-cafe-pro -b chrome:headless -f signup.js
```

### Restore DB

Pour restorer un fichier de dump postgresql (file.pgdump) en local:

```bash
pc restore-db file.pgdump
```

Pour anonymiser les données après restauration, et changer le mot de passe pour tout les users :

```bash
./api/scalingo/anonymize_database.sh -p PASSWORD
```

### Database de jeu

Afin de naviguer/tester différentes situations de données, il existe dans api des scripts permettant d'engendrer des bases de données "sandbox".

La plus conséquente est l'industrial, elle se créée via la commande:

```bash
pc sandbox -n industrial
```

---

Troubleshooting:

Si la commande sandbox renvoie des erreurs que je n'arrive pas à résoudre, tester de supprimer et reconstruire sa BDD locale. Pour ça:

- stopper les images lancées
- run: `docker rm -f pc-postgres` <= suppression container
- run: `docker volume rm pass-culture-main_postgres_data` <= suppression données
- relancer: `pc start-backend`
- puis relancer: `pc sandbox -n industrial`

---

Pour l'application WEBAPP, vous pouvez naviguer avec ce user toujours présent:

```
email: pctest.jeune93.has-booked-some@example.com
```

Pour l'application PRO, vous pouvez naviguer en tant qu'admin avec:

```
email: pctest.admin93.0@example.com
```

Ou en tant qu'user avec :

```
email: pctest.pro93.0@example.com
```

Le mot de passe est toujours : `user@AZERTY123`

(Ces deux utilisateurs existent également pour le 97, pour les utiliser, il suffit de remplacer 93 par 97)

### Commandes utiles

- Rebuild : `pc rebuild-backend` (reconstruire l'image docker sans cache)
- Restart : `pc restart-backend` (effacer la base de données, et relancer tous les containers)
- Reset :
  - `pc reset-sandbox-db` : si vos serveurs de dev tournent, et que vous souhaitez juste réinitialiser la db
  - `pc reset-reco-db` : (si vous voulez juste enlever les recommandations et bookings créés en dev par votre navigation)

## Deploiement

### Testing

Le déploiement se lance lors d'un merge sur la branche `master` pour les 4 repos :

- api : [configuration circlecI](api/.circleci/config.yml)
- pro : [configuration circlecI](pro/.circleci/config.yml)
- webapp : [configuration circlecI](webapp/.circleci/config.yml)
- adage-front : [configuration circlecI](adage-front/.circleci/config.yml)

Pré-requis : installer [jq](https://stedolan.github.io/jq/download/)

### Staging et Production

Le déploiement en staging et production suit les étapes suivantes :

1.  Tagging de la version : [lire plus bas](#tagging-des-versions)
2.  Déploiement du tag en `staging`
3.  Tests de la version déployée en `staging`
4.  Déploiement du tag en `production`
5.  Déploiement du tag en `integration`

Les 5 repos suivants sont taggés et déployés simultanément :

- `api`
- `pro`
- `webapp`
- `doc`
- `adage-front`

Une fois le tag posé (les tests doivent être **verts**) réaliser le déploiement avec la commande

```bash
pc -e <staging|production|integration> -t {numéro_de_version} deploy
```

Par exemple pour déployer la version 138.0.0 en staging :

```bash
pc -e staging -t 138.0.0 deploy
```

A la fin de l'opération, une fenêtre de votre navigateur s'ouvrira sur le workflow en cours.

Après avoir livré en production, ne pas oublier de livrer ensuite sur les environnements d'integration.

### Tagging des versions

_Poser un tag_ consiste à sélectionner un ensemble de commits et de leur attribuer un numéro de version.

1. Checkout master sur tous les submodules

- `git submodule foreach git checkout master && git submodule foreach git pull`


La seule branche devant être taguée de cette façon est master. Pour les hotfixes, [voir plus bas](#hot-fixes).

2. Lancer la commande

```bash
pc -t {numéro_de_version} tag
```

Par exemple

```bash
pc -t 138.0.0 tag
```

3. Sur CircleCI, vérifier l'avancement du job sur `main`.

### Numéro de version

Pour déterminer le numéro de version

- On n'utilise pas de _semantic versioning_
- On utilise le format `I.P.S`
  - I => numéro de l'**Itération**
  - P => incrément de _fix_ en **Production**
  - S => incrément de _fix_ en **Staging**
- Lors de la pose d'un tag, il faut communiquer les migrations de BDD embarquées à la data pour éviter des bugs sur les analytics

#### Exemple

- Je livre une nouvelle version en staging en fin d'itération n°20 => `20.0.0`
- Je m'aperçois qu'il y a un bug en staging => `20.0.1`
- Le bug est corrigé, je livre en production => `20.0.1`
- On détecte un bug en production, je livre en staging => `20.1.0`
- Tout se passe bien en staging, je livre en production => `20.1.0`
- On détecte un autre bug en production, je livre en staging => `20.2.0`
- Je m'aperçois que mon fix est lui-même buggé, je relivre un fix en staging => `20.2.1`
- Mes deux fix sont cette fois OK, je livre en production => `20.2.1`

Le fichier version.txt de l'API est mis à jours ainsi que le package.json de Webapp, Pro et dage-front.
Le tag est posé sur les branches locales checkout (de préférence master): Api, Webapp, Pro et adage-front.
Elles sont ensuite poussées sur le repository distant.
Les tests sont enfin joués et on déploie sur staging.

### Hot fixes

Faire un hotfix consiste à créer un nouveau tag à partir du tag précédents avec des commits spécifiques.

1. Les commits sont poussés sur `master`, déployés sur testing et validés par les POs
2. Se placer en local sur le dernier tag

- repo main : `git checkout v{numero_de_version}`
- repo api : `git checkout v{numero_de_version}`
- repo pro : `git checkout v{numero_de_version}`
- repo webapp : `git checkout v{numero_de_version}`
- repo adage-front : `git checkout v{numero_de_version}`

3. Cherry-pick les commits voulus

Exemple :

```
cd api && git cherry-pick 3e07b9420e93a2a560b2deec1aed2e983fc842e8
```

4. Lancer la commande de création de tag hot fix :

```bash
pc -t {numero_de_version_incrémenté} tag-hotfix
```

Une fois les tests de la CI passés, on peut déployer ce tag.
Il faut aussi penser à supprimer les branches de hotfixs une fois le déploiement passé.

## Administration

### Connexion à la base postgreSQL d'un environnement

```bash
pc -e <testing|staging|production> psql
```

ou

```bash
pc -e <testing|staging|production> pgcli
```

### Connexion à la base postgreSQL en local

```bash
pc psql
```

ou

```bash
pc pgcli
```

### Configuration de Metabase

```bash
pc start-metabase
```

Lance Metabase et une base de données contenant les données sandbox du produit.
Pour supprimer les volumes avant de lancer Metabase, utiliser la commande :

```bash
pc restart-metabase
```

L'url pour aller sur Metabase en local est : http://localhost:3002/

Pour configurer Metabase, il suffit de créer un compte admin, puis de se connecter à la base produit. Pour cela, il faut renseigner les informations suivantes :

- Host : pc-postgres-product-metabase
- Port : 5432
- Database name : pass_culture
- Database username : pass_culture
- Database password : passq

### Connexion en ligne de commande python à un environnement (testing | staging | production)

```bash
pc -e <testing|staging|production> python
```

Il est également possible d'uploader un fichier dans l'environnement temporaire grâce à la commande suivante :

```bash
pc -e <testing|staging|production> -f myfile.extension python
```

L'option -f est également disponible pour la commande bash :

```bash
pc -e <testing|staging|production> -f myfile.extension bash
```

Le fichier se trouve à l'emplacement `/tmp/uploads/myfile.extension`

### Acceder au logs des bases de données

En local :

```bash
pc access-db-logs
```

Sur les autres environnements :

```bash
pc -e <testing|staging|production> access-db-logs
```

### Gestion des objects storage OVH

Pour toutes les commandes suivantes, vous devez disposer des secrets de connexion.

Pour lister le contenu d'un conteneur spécifique :

```bash
pc list_content --container=storage-pc-staging
```

Pour savoir si une image existe au sein d'un conteneur :

```bash
pc does_file_exist --container=storage-pc-staging --file="thumbs/venues/SM"
```

Pour supprimer une image au sein d'un conteneur :

```bash
pc delete_file --container=storage-pc-staging --file="thumbs/venues/SM"
```

Pour faire un backup de tous les fichiers du conteneur de production vers un dossier local :

```bash
pc backup_prod_object_storage --container=storage-pc --folder="~/backup-images-prod"
```

Pour copier tous les fichiers du conteneur de production vers le conteneur d'un autre environnement :

```bash
pc copy_prod_container_content_to_dest_container --container=storage-pc-staging
```

## Gestion OVH

#### CREDENTIALS

Vérifier déjà que l'un des admins (comme @arnoo) a enregistré votre adresse ip FIXE (comment connaitre son adresse ip? http://www.whatsmyip.org/)

#### Se connecter à la machine OVH d'un environnement

```bash
pc -e <testing|staging|production> ssh
```

### Dump Prod To Staging

ssh to the prod server

```bash
cd ~/pass-culture-main && pc dump-prod-db-to-staging
```

Then connect to the staging server:

```bash
cd ~/pass-culture-main
cat "../dumps_prod/2018_<TBD>_<TBD>.pgdump" docker exec -i docker ps | grep postgres | cut -d" " -f 1 pg_restore -d pass_culture -U pass_culture -c -vvvv
pc update-db
pc sandbox --name=webapp
```

### Updater le dossier private

Renseigner la variable d'environnement PC_GPG_PRIVATE.
Puis lancer la commande suivante :

```bash
pc install-private
```

#### Updater la db

Une fois connecté:

```
cd /home/deploy/pass-culture-main/ && pc update-db
```

#### Note pour une premiere configuration HTTPS (pour un premier build)

Pour obtenir un certificat et le mettre dans le nginx (remplacer <domaine> par le domaine souhaité, qui doit pointer vers la machine hébergeant les docker)

```bash
docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt -v ~/pass-culture-main/certs-data:/data/letsencrypt deliverous/certbot certonly --verbose --webroot --webroot-path=/data/letsencrypt -d <domaine>
```

Puis mettre dans le crontab pour le renouvellement :

```bash
docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt -v ~/pass-culture-main/certs-data:/data/letsencrypt deliverous/certbot renew --verbose --webroot --webroot-path=/data/letsencrypt
```

## Lancer les tests de performance

### Environnement

Les tests requièrent d'avoir un environnement spécifique sur Scalingo, ici `pass-culture-api-perf`, comportant notamment une base utilisateur.
Pour la remplir, il faut jouer les sandboxes `industrial` et `activation`.

Execution des sandboxes sur le conteneur :

```bash
scalingo -a pass-culture-api-perf --region osc-fr1 run 'python src/pcapi/scripts/pc.py sandbox -n industrial'
scalingo -a pass-culture-api-perf --region osc-fr1 run 'python src/pcapi/scripts/pc.py sandbox -n activation'
```

Ensuite, lancer le script d'import des utilisateurs avec une liste d'utilisateurs en csv prédéfinie placée dans le dossier `artillery` sous le nom `user_list`.
On passe en paramètre un faux email qui ne sera pas utilisé.

````bash
scalingo -a pass-culture-api-perf --region osc-fr1 run 'ACTIVATION_USER_RECIPIENTS=<email> python /tmp/uploads/import_users.py user_list' -f scalingo/import_users.py -f user_list```
````

Un exemple de csv utilisateur `user_list` :

```bash
1709,Patricia,Chadwick,ac@enimo.com,0155819967,Drancy (93),16282,2001-05-17,secure_password
```

### Lancement d'un scénario

Pour lancer les tests de performance il faut installer le logiciel `artillery` : `npm install -g artillery` et son plugin `metrics-by-endpoint` : `npm install artillery-plugin-statsd`, puis se munir du fichier csv contenant
les users valides.

Puis se placer dans le dossier `artillery` et lancer la commande :

```bash
artillery run scenario.yml -o reports/report-$(date -u +"%Y-%m-%dT%H:%M:%SZ").json
```

Un rapport des tests daté sera généré dans le sous-dossier `reports` (qui doit être crée).
