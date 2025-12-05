<div align=center>
  <img src="https://storage.googleapis.com/passculture-metier-prod-production-assets-fine-grained/assets/passculture.gif" style="width: 360px">
  <br />
  <a href="https://apps.apple.com/fr/app/pass-culture/id1557887412">
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/40/Download_on_the_App_Store_Badge_FRCA_RGB_blk.svg" style="height: 50px">
  </a>
  <a href="https://play.google.com/store/apps/details?id=app.passculture.webapp&hl=fr">
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/8e/Google_Play_Store_badge_FR.svg" style="height: 50px; padding-left: 12px">
  </a>
</div>

---
Le repo `main` contient les 4 projets suivants :

- Le backend : [api](./api) (Flask)
- L'espace partenaire : [pro](./pro) (React)
- La documentation de l'API publique pour les partenaires techniques du pass Culture : [doc](./api/documentation)
- La page de maintenance (HTML):  [maintenance-site](./maintenance-site)

## Installation

#### Installer les bibliothèques

- Docker
  - [docker](https://docs.docker.com/install/) (testé avec 19.03.12)
  - [docker compose (inclus avec Docker Desktop)](https://docs.docker.com/compose/install/#install-compose) (testé avec 1.26.2)
- [NVM](https://github.com/creationix/nvm) (Node Version Manager)
  - `curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash`
- [Node](https://nodejs.org/en/download/)
  - Lancer `nvm install` dans `/pro`
- [safe-chain](https://www.npmjs.com/package/@aikidosec/safe-chain)
  - `npm i -g @aikidosec/safe-chain`
  - `safe-chain setup`
  - Redémarrer le terminal
- [Yarn](https://classic.yarnpkg.com/en/)
  - `npm install --global yarn` (NPM)
  - autres méthodes [dans la doc de Yarn](https://classic.yarnpkg.com/lang/en/docs/install/)

- [Commitizen](https://commitizen-tools.github.io/commitizen/#installation) (CLI pour écrire des commits au bon format)
  - `pip install -U commitizen` ou `brew install commitizen`

- [gitleaks](https://github.com/gitleaks/gitleaks)
  - `brew install gitleaks`

Pour les devs **qui n'utilisent PAS VSCode** et qui ouvrent le projet à partir du dossier racine `pass-culture-main` dans leur IDE :
- [Biome](https://biomejs.dev/guides/getting-started/) (Linter JS/JSON/CSS/HTML pour le Frontend)
  - `npm i -g @biomejs/biome` ou `brew install biome`
  - Installer l'[extension correspondant à ton IDE si dispo](https://biomejs.dev/guides/editors/first-party-extensions/)
  - Prendre garde à ce que ta version Biome globale soit la même que celle déclarée dans les dev-deps `pro/package.json`.

- Pour MacOS spécifiquement :
  - CoreUtils: `brew install coreutils libxmlsec1`
- Pour Linux spécifiquement :
  - L'API a besoin des paquets suivants, à installer avec `sudo apt install python3-dev libpq-dev xmlsec1 libpango-1.0-0 libpangoft2-1.0-0` pour les distributions Ubuntu

#### Installer les CLI

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
docker compose. On trouvera dans le [README](./api#readme) d'`api` d'autres
manières de lancer le backend.

#### api

- `pc start-backend`
- `pc sandbox -n industrial` (pour peupler la DB)

Le backend est accessible sur [http://localhost:5001/](http://localhost:5001/), il est possible d'en tester le
fonctionnement par la route [http://localhost:5001/health/api](http://localhost:5001/health/api).

#### Backoffice

- [http://localhost:5002/](http://localhost:5002/) devrait être lancé et fonctionnel après `pc start-backend`, une fois
qu'api répond
- Cliquez sur _Se connecter via Google_
- Vous arriverez alors sur la page d'accueil du BO, en tant qu'utilisateur admin `admin@passculture.local`, avec toutes
les permissions
- Si vous avez besoin d'une adresse email spécifique pour l'admin local, par exemple pour le lien avec des services 
externes, spécifiez l'email dans une variable `BACKOFFICE_LOCAL_USER_EMAIL` dans le fichier `.env.local.secret`. 


#### pro

- `pc start-pro`
- [http://localhost:3001/](http://localhost:3001/) devrait être lancé et fonctionnel
- Connectez-vous avec `pctest.admin93.0@example.com` (admin) ou `pctest.pro93.0@example.com` (non-admin)

Le mot de passe des utilisateurs de la sandbox dans un environnement de développement est : `user@AZERTY123`

L'environnement de test déployé dans le cloud (_testing_) utilise un mot de passe secret par souci de protection
des données manipulées lors des tests ; en interne, le mot de passe « PRO - testing » est disponible dans le coffre-fort
de l'équipe.

Ces utilisateurs existent également pour le 97, en remplaçant `93` par `97`.

D'autres informations sont disponibles sur le [README de Pro](./pro/README.md)

### Lancer les tests sur VSCode

#### Tests back

Il est possible de lancer / débugger les tests python directement depuis VSCode. Pour cela il faut avoir installé les extensions `ms-python.python` et `ms-python.debugpy`.

On peut voir la liste des tests dans l'onglet Testing, où l'on peut lancer les tests par fonction / classe / fichier / dossier. Lorsqu'on est dans un fichier de test, on peut également utiliser les icones placées directement à côté de chaque fonction.

Quelques commandes VSCode utiles lorsqu'on est dans un fichier de test, avec leur équivalent `Debug Test` :
- `Test: Run Test in Current File`
- `Test: Run Test at Cursor`
- `Test: Rerun Last Run`
- `Test: Rerun Failed Tests`

Voir https://code.visualstudio.com/docs/python/testing pour plus d'informations.

#### Tests front

De la même manière pour les tests front, il faut cette fois installer l'extension `vitest.explorer`. On aura alors accès aux tests des fichiers `*.spec.tsx` dans l'onglet Testing.

On peut également utiliser la commande de launch `Debug current spec test file`. Lorsqu'on est dans un fichier `*.spec.tsx`, on peut lancer la commande depuis l'onglet `Run and Debug` et les tests du fichier seront exécutés.

### Commandes utiles

- Rebuild : `pc rebuild-backend` (reconstruire l'image docker sans cache)
- Restart : `pc restart-backend` (effacer la base de données, et relancer tous les containers)
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

La branche `master` est déployée sur testing toutes les heures.

### Déployer dans un environnement de preview

Il est nécessaire d'avoir la [CLI de github](https://cli.github.com/) installée.

Pour déployer dans un environnement de preview, utilisez la commande `pc deploy-preview` (documentation complète dans le script [pc](./pc))


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

### Connexion en ligne de commande python à un environnement (testing | staging | production | integration)

```bash
pc -e <testing|staging|production|integration> python
```

### Téléverser un fichier

Il est également possible d'uploader un fichier dans l'environnement temporaire à
l'emplacement `/usr/src/app/myfile.extension`

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
