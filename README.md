# pass-culture-main

Le repo `main` contient les 6 sous-modules suivants :

- l'[api](https://github.com/pass-culture/pass-culture-api) (Flask)
- le portail [pro](https://github.com/pass-culture/pass-culture-pro) (React), pour les acteurs culturels
- la [webapp](https://github.com/pass-culture/pass-culture-browser) (React) : version web de l'application des jeunes,
  remplacée progressivement par l'[app native](https://github.com/pass-culture/pass-culture-app-native/)
- [adage-front](https://github.com/pass-culture/pass-culture-adage-front) (React), application frontend pour les
  rédacteurs de projets scolaires
- [doc](https://github.com/pass-culture/pass-culture-doc) : documentation de l'API pour les partenaires du pass Culture
- [maintenance-api](https://github.com/pass-culture/pc-maintenance) : page de maintenance (HTML)

## Installation

#### Installer les bibliothèques

- Docker
    - [docker](https://docs.docker.com/install/) (testé avec 19.03.12)
    - [docker-compose](https://docs.docker.com/compose/install/#install-compose) (testé avec 1.26.2)
- [NVM](https://github.com/creationix/nvm) (Node Version Manager)
    - `curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash`
- [Node](https://nodejs.org/en/download/)
    - Lancer `nvm install` dans `/pro` et `/webapp`
- [Yarn](https://classic.yarnpkg.com/en/)
    - `npm install --global yarn` (NPM)
    - autres méthodes [dans la doc de Yarn](https://classic.yarnpkg.com/lang/en/docs/install/)
- GPG (outil de (dé)chiffrement)
    - [GPG Suite](https://gpgtools.org/) (MacOS)
    - `sudo apt install gpg` (Linux)

- Pour MacOS spécifiquement
    - CoreUtils: `brew install coreutils`

#### Installer les CLI

- Netlify: `npm install -g netlify-cli@1.2.3`
- [kubectl](https://kubectl.docs.kubernetes.io/installation/kubectl/)
- [gcloud](https://cloud.google.com/sdk/docs/install)

#### Installer l'ensemble des projets

Il vous faudra une clé SSH sur votre profil GitHub pour pouvoir cloner le repository.

1. `git clone git@github.com:pass-culture/pass-culture-main.git pass-culture-main`
2. `cd pass-culture-main`
3. `git submodule update --init --recursive`
4. `./pc symlink`
5. `pc install`

Les README de chaque sous-module détailleront leurs installations spécifiques.

### Lancer les applications

Voici de brèves instructions pour lancer l'API et les différents frontends via le script `pc`, qui fait appel à
docker-compose. On trouvera dans le [README](https://github.com/pass-culture/pass-culture-api#readme) d'`api` d'autres
manières de lancer le backend.

#### api

- `pc start-backend`
- `pc sandbox -n industrial` (pour peupler la DB)

#### webapp

- `pc start-webapp`
- `http://localhost:3000/` devrait être lancé et fonctionnel
- Connectez-vous avec `pctest.jeune93.has-booked-some.v1@example.com`

#### pro

- `pc start-pro`
- `http://localhost:3001/` devrait être lancé et fonctionnel
- Connectez-vous avec `pctest.admin93.0@example.com` (admin) ou `pctest.pro93.0@example.com` (non-admin)

#### adage-front

- `pc start-adage-front`
- `http://localhost:3002/` devrait être lancé et fonctionnel
- Connectez-vous avec un token valide en le passant en query param (pour générer un token valide, générez-le via le
  helper de test dans l'API)

#### Flask Admin

- lancer `api`, et `pro` ou `webapp`
- se connecter avec les identifiants d'un compte admin, par exemple `pctest.admin93.0@example.com`
- visiter `http://localhost/pc/back-office/`

Le mot de passe des utilisateurs de la sandbox est : `user@AZERTY123`

Ces utilisateurs existent également pour le 97, en remplaçant `93` par `97`.

### Commandes utiles

- Rebuild : `pc rebuild-backend` (reconstruire l'image docker sans cache)
- Restart : `pc restart-backend` (effacer la base de données, et relancer tous les containers)
- Reset :
    - `pc reset-sandbox-db` : si vos serveurs de dev tournent, et que vous souhaitez juste réinitialiser la db
    - `pc reset-reco-db` : (si vous voulez juste enlever les recommandations et bookings créés en dev par votre
      navigation)
- Restore : `pc restore-db file.pgdump` (restaurer un fichier de dump postgresql (file.pgdump) en local)

#### Troubleshooting:

Si la commande sandbox renvoie des erreurs que je n'arrive pas à résoudre, on peut essayer de supprimer et reconstruire
sa BDD locale via `pc restart-backend`. Sinon:

- stopper les images lancées
- `docker rm -f pc-postgres` <= suppression container
- `docker volume rm pass-culture-main_postgres_data` <= suppression données
- `pc start-backend`
- `pc sandbox -n industrial`

## Livrer

### Tagging des versions

Poser un _tag_ consiste à sélectionner un ensemble de commits et de leur attribuer un numéro de version.

1. Checkout `master` sur tous les submodules

- `git submodule foreach git checkout master && git submodule foreach git pull`

La seule branche devant être _taggée_ de cette façon est `master`. Pour les hotfixes, [voir plus bas](#hot-fixes).

2. Lancer la commande

```bash
pc -t {numéro_de_version} tag
```

Par exemple

```bash
pc -t 138.0.0 tag
```

Le fichier `version.txt` de l'API est mis à jours ainsi que les `package.json` de Webapp, Pro et Adage-front. Le tag est
posé sur les branches locales _checked out_ (de préférence master): Api, Webapp, Pro et adage-front. Il est ensuite
poussé sur le repository distant. La CI lance alors des pipelines de tests.

3. Sur [CircleCI](https://app.circleci.com/pipelines/github/pass-culture/pass-culture-main), vérifier l'avancement du
   pipeline de `pass-culture-main`.

### Numéro de version

- On n'utilise **pas** de _semantic versioning_
- On utilise le format `I.P.S`
    - I => numéro de l'**Itération**
    - P => incrément de _fix_ en **Production**
    - S => incrément de _fix_ en **Staging**
- En amont de la pose d'un tag, il faut communiquer les migrations de BDD embarquées à l'équipe data pour éviter des
  bugs sur les analytics

#### Exemple

- Jeudi, je livre en staging une nouvelle version en fin d'itération n°138 => `138.0.0`
- Vendredi, un bug est détecté en staging, et je livre un correctif => `138.0.1`
- Lundi, je livre en production => `138.0.1`
- Mardi, on détecte un bug en production, je livre d'abord le correctif en staging => `138.1.0`
- Mardi, tout se passe bien en staging, je livre en production => `138.1.0`
- Jeudi, je livre en staging une nouvelle version en fin d'itération n°139 => `139.0.0`
- Jeudi, on détecte un autre bug de la v138 en production, je livre d'abord en staging => `138.2.0`
- Vendredi, je m'aperçois que mon fix est lui-même buggé, je livre un fix en staging => `138.2.1`
- Vendredi, mes deux correctifs sont cette fois OK, je livre en production => `138.2.1`
  et on déploie sur staging.

### Hotfixes

Faire un hotfix consiste à créer un nouveau tag à partir du tag précédent avec des commits spécifiques.

1. Vérifier que les commits sont poussés sur `master`, déployés sur testing et validés par les POs
2. Se placer en local sur le dernier tag

- repo main : `git checkout v{numero_de_version}`
- repo api : `git checkout v{numero_de_version}`
- repo pro : `git checkout v{numero_de_version}`
- repo webapp : `git checkout v{numero_de_version}`
- repo adage-front : `git checkout v{numero_de_version}`

3. Butiner les commits désirés, sur chaque repo

Exemple :

```
cd api && git cherry-pick 3e07b9420e93a2a560b2deec1aed2e983fc842e8
cd ../pro && git cherry-pick c3eaa9395cfa9bc5b48d78256b9693af56cbc1d0
```

4. Lancer la commande de création de tag hot fix :

```bash
pc -t {numero_de_version_incrémenté} tag-hotfix
```

Une fois les tests de la CI passés, on peut déployer ce tag.

5. Supprimer les branches de hotfix une fois les déploiements réussis.

### Déployer dans l'environnement Testing

Le déploiement se lance automatiquement lors d'un _merge_ sur la branche `master` pour les 4 repos :

- api : [configuration circlecI](api/.circleci/config.yml)
- pro : [configuration circlecI](pro/.circleci/config.yml)
- webapp : [configuration circlecI](webapp/.circleci/config.yml)
- adage-front : [configuration circlecI](adage-front/.circleci/config.yml)

Pré-requis : installer [jq](https://stedolan.github.io/jq/download/)

### Déployer dans les environnements Staging, Production et Integration

#### Processus de livraison

1. Tagging de la version : [lire plus haut](#tagging-des-versions)
2. Déploiement du tag en `staging`
3. Tests de la version déployée en `staging`
4. Déploiement du tag en `production`
5. Déploiement du tag en `integration`

Les 5 repos suivants sont taggés ou déployés simultanément :

- `api`
- `pro`
- `webapp`
- `doc`
- `adage-front`

Une fois le tag posé, on vérifie que les tests sont bien en succès, puis on lance le déploiement avec la commande

```bash
pc -e <staging|production|integration> -t {numéro_de_version} deploy
```

Par exemple pour déployer la version 138.0.0 en staging :

```bash
pc -e staging -t 138.0.0 deploy
```

A la fin de l'opération, une fenêtre de votre navigateur s'ouvrira sur le pipeline en cours.

Après avoir livré en production, ne pas oublier de livrer ensuite sur l' environnement **integration**.

## Administration

### Connexion à la base postgreSQL d'un environnement

```bash
pc -e <testing|staging|production|integration> psql
```

ou

```bash
pc -e <testing|staging|production|integration> pgcli
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

Lance Metabase et une base de données contenant les données sandbox du produit. Pour supprimer les volumes avant de
lancer Metabase, utiliser la commande :

```bash
pc restart-metabase
```

L'url pour aller sur Metabase en local est : http://localhost:3002/

Pour configurer Metabase, il suffit de créer un compte admin, puis de se connecter à la base produit. Pour cela, il faut
renseigner les informations suivantes :

- Host : pc-postgres-product-metabase
- Port : 5432
- Database name : pass_culture
- Database username : pass_culture
- Database password : passq

### Connexion en ligne de commande python à un environnement (testing | staging | production | integration)

```bash
pc -e <testing|staging|production|integration> python
```

### Téléverser un fichier

Il est également possible d'uploader un fichier dans l'environnement temporaire à
l'emplacement `/tmp/uploads/myfile.extension`

```bash
pc -e <testing|staging|production|integration> -f myfile.extension python
```

```bash
pc -e <testing|staging|production|integration> -f myfile.extension bash
```

### Accéder aux logs des bases de données

En local :

```bash
pc access-db-logs
```

Sur les autres environnements :

```bash
pc -e <testing|staging|production> access-db-logs
```
