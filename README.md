<div align=center>
  <img src="https://pass.culture.fr/wp-content/uploads/2020/11/RVB_PASS_CULTURE_HD.png" style="width: 360px">
  <br />
  <a href="https://apps.apple.com/fr/app/pass-culture/id1557887412">
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/40/Download_on_the_App_Store_Badge_FRCA_RGB_blk.svg" style="height: 50px">
  </a>

  <a href="https://play.google.com/store/apps/details?id=app.passculture.webapp&hl=fr">
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/8e/Google_Play_Store_badge_FR.svg" style="height: 50px; padding-left: 12px">
  </a>
</div>

---
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=pass-culture_pass-culture-main&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=pass-culture_pass-culture-main) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=pass-culture_pass-culture-main&metric=coverage)](https://sonarcloud.io/summary/new_code?id=pass-culture_pass-culture-main)

[![Testing Environement](https://img.shields.io/github/deployments/pass-culture/pass-culture-main/testing?label=Testing%20Environment)](https://github.com/pass-culture/pass-culture-main/deployments/activity_log?environment=testing)

[![Tag](https://img.shields.io/github/v/tag/pass-culture/pass-culture-main)](https://github.com/pass-culture/pass-culture-main/tags)

Le repo `main` contient les 5 projets suivants :

- l'[api](./api/) (Flask)
- le portail [pro](./pro) (React), pour les acteurs culturels
- [adage-front](./adage-front) (React, TS), application frontend pour les
  rédacteurs de projets scolaires
- [doc](./doc) : documentation de l'API pour les partenaires du pass Culture
- [maintenance-api](./maintenance-ste) : page de maintenance (HTML)

## Installation

#### Installer les bibliothèques

- Docker
  - [docker](https://docs.docker.com/install/) (testé avec 19.03.12)
  - [docker-compose](https://docs.docker.com/compose/install/#install-compose) (testé avec 1.26.2)
- [NVM](https://github.com/creationix/nvm) (Node Version Manager)
  - `curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash`
- [Node](https://nodejs.org/en/download/)
  - Lancer `nvm install` dans `/pro` et `/adage-front`
- [Yarn](https://classic.yarnpkg.com/en/)
  - `npm install --global yarn` (NPM)
  - autres méthodes [dans la doc de Yarn](https://classic.yarnpkg.com/lang/en/docs/install/)
- GPG (outil de (dé)chiffrement)

  - [GPG Suite](https://gpgtools.org/) (MacOS)
  - `sudo apt install gpg` (Linux)

- [Commitizen](https://commitizen-tools.github.io/commitizen/#installation) (CLI pour écrire des commits au bon format)

  - `pip install -U commitizen` ou `brew install commitizen`

- Pour MacOS spécifiquement
  - CoreUtils: `brew install coreutils libxmlsec1`
- Pour Linux spécifiquement
  - L'API a besoin des paquets suivants, à installer avec `sudo apt install python3-dev libpq-dev xmlsec1 libpango-1.0-0 libpangoft2-1.0-0` pour les distributions Ubuntu

#### Installer les CLI

- Netlify: `npm install -g netlify-cli@1.2.3`
- [kubectl](https://kubectl.docs.kubernetes.io/installation/kubectl/)
- [gcloud](https://cloud.google.com/sdk/docs/install)

#### Installer l'ensemble des projets

Il vous faudra une clé SSH sur votre profil GitHub pour pouvoir cloner le repository.

1. `git clone git@github.com:pass-culture/pass-culture-main.git pass-culture-main`
2. `cd pass-culture-main`
3. `./pc symlink`
4. `pc install`

Les README de chaque sous-projet détailleront leurs installations spécifiques.

### Lancer les applications

Voici de brèves instructions pour lancer l'API et les différents frontends via le script `pc`, qui fait appel à
docker-compose. On trouvera dans le [README](./api#readme) d'`api` d'autres
manières de lancer le backend.

#### api

- `pc start-backend`
- `pc sandbox -n industrial` (pour peupler la DB)

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

- lancer `api` ou `pro`
- se connecter avec les identifiants d'un compte admin, par exemple `pctest.admin93.0@example.com`
- visiter `http://localhost/pc/back-office/`

Le mot de passe des utilisateurs de la sandbox dans un environnement de développement est : `user@AZERTY123`

L'environnement de test déployé dans le cloud (_testing_) utilise un mot de passe secret par souci de protection
des données manipulées lors des tests ; en interne, le mot de passe « PRO - testing » est disponible dans le coffre-fort
de l'équipe.

Ces utilisateurs existent également pour le 97, en remplaçant `93` par `97`.


#### Backoffice v3

- `pc start-backoffice`
- `http://localhost:5001/backofficev3/` devrait être lancé et fonctionnel
- Cliquez sur _Se connecter via Google_
- Vous arriverez alors sur la page d'accueil du BO v3, en tant qu'utilisateur admin `admin@passculture.local`

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

## Déploiement


### Déployer dans l'environnement Testing

Le déploiement se lance automatiquement lors d'un _merge_ sur la branche `master`

Pré-requis : installer [jq](https://stedolan.github.io/jq/download/)

### Déployer dans les environnements Staging, Production et Integration

Le déploiement se fait à partir d'actions github (notamment `release--build`, `release--deploy.yml`, `release--build.yml`, `release--build-hotfix.yml`) et est documenté sur Notion (article Tag-MES-et-MEP).

Pour connaître le numéro de version de l'api déployé :

```
https://backend.staging.passculture.team/health/api
https://backend.passculture.app/health/api
```

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
