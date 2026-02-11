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

### Installer les dépendances communes entre le front pro et le backend

- [safe-chain](https://www.npmjs.com/package/@aikidosec/safe-chain)  # TODO: tester l'installation avec safe-chain
  - `npm i -g @aikidosec/safe-chain`
  - `safe-chain setup`
  - Redémarrer le terminal

- [Commitizen](https://commitizen-tools.github.io/commitizen/#installation) (CLI pour écrire des commits au bon format)
  - `brew install commitizen`

- [gitleaks](https://github.com/gitleaks/gitleaks)
  - `brew install gitleaks`

### Installer l'ensemble des projets

Il vous faudra une clé SSH sur votre profil GitHub pour pouvoir cloner le repository.

1. `git clone git@github.com:pass-culture/pass-culture-main.git pass-culture-main`
2. `cd pass-culture-main`
3. `sudo ./pc symlink`
4. `pc install`

Les README de chaque sous-projet détailleront leurs installations spécifiques.

- [README.md api](./api#readme)
- [README.md pro](./pro#readme)

### Lancer les applications via le script `pc`

Il est recommandé de lire les READMEs dans le paragraphe au dessus pour l'installation et le lancement
des serveurs. Cependant, si vous êtes à 5 minutes près, voici de brèves instructions pour lancer l'API et les différents frontends via le script `pc`, qui fait appel à docker compose.

Le script `pc` n'est pas essentiel au projet, il est toujours possible de lancer les serveurs directement en
utilisant les commandes `python` ou `yarn`.

#### Backend api

Via docker et le script `pc` :

- [docker](https://docs.docker.com/install/) (testé avec 19.03.12)
- [docker compose (inclus avec Docker Desktop)](https://docs.docker.com/compose/install/#install-compose) (testé avec 1.26.2)

- `pc start-backend` ou `pc start-backend --fast` ou `pc start-proxy-backend` ou `pc start-proxy-backend --fast`
- `pc sandbox -n industrial` (pour peupler la DB)

Le backend est accessible sur [http://localhost:5001/](http://localhost:5001/), il est possible d'en tester le
fonctionnement par la route [http://localhost:5001/health/api](http://localhost:5001/health/api).

Un grand désavantage de passer par docker est la latence et la durée de création de l'image. On trouvera dans le [README](./api#readme) d'`api` d'autres manières de lancer le backend.

#### Backoffice

- [http://localhost:5002/](http://localhost:5002/) devrait être lancé et fonctionnel après `pc start-backend`, une fois
qu'api répond
- Cliquez sur _Se connecter via Google_
- Vous arriverez alors sur la page d'accueil du BO, en tant qu'utilisateur admin `admin@passculture.local`, avec toutes
les permissions
- Si vous avez besoin d'une adresse email spécifique pour l'admin local, par exemple pour le lien avec des services
externes, spécifiez l'email dans une variable `BACKOFFICE_LOCAL_USER_EMAIL` dans le fichier `.env.local.secret`.

#### Portail pro

- `pc start-pro`
- [http://localhost:3001/](http://localhost:3001/) devrait être lancé et fonctionnel
- Connectez-vous avec `pctest.admin93.0@example.com` (admin) ou `pctest.pro93.0@example.com` (non-admin)

Le mot de passe des utilisateurs de la sandbox dans un environnement de développement est : `user@AZERTY123`

L'environnement de test déployé dans le cloud (_testing_) utilise un mot de passe secret par souci de protection
des données manipulées lors des tests ; en interne, le mot de passe « PRO - testing » est disponible dans le coffre-fort
de l'équipe.

Ces utilisateurs existent également pour le 97, en remplaçant `93` par `97`.

D'autres informations sont disponibles sur le [README de Pro](./pro/README.md)

### Commandes utiles

- Rebuild : `pc rebuild-backend` (reconstruire l'image docker sans cache)
- Restart : `pc restart-backend` (effacer la base de données, et relancer tous les containers)
- Restore : `pc restore-db file.pgdump` (restaurer un fichier de dump postgresql (file.pgdump) en local)

### Troubleshooting

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

## Administration  # TODO: migrer la documentation à la nouvelle infra

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
