# pass-culture-main

C'est tout le framework du Pass Culture!

## Minimal Process

### Install

Il vous faudra une machine UNIX.

Installer:
- [docker](https://docs.docker.com/install/)
- [docker-compose](https://docs.docker.com/compose/install/#install-compose)
- [yarn](https://yarnpkg.com/fr/) voir le README dans le dépot https://github.com/betagouv/pass-culture-browser/

Mais spécialement, en plus pour macosx:
- brew install coreutils


Enfin pour tout le monde:
```bash
pc install
```
Le script `pc` sera automatiquement lié dans votre dossier `/usr/local/bin`

### Init
Pour verifier les tests et obtenir une db minimale:
```bash
pc test-backend
```

### Démarrage

Pour lancer l'API:
```bash
pc start-backend
```

Pour lancer l'appli Web:
```bash
pc start-webapp
```

Pour lancer le portail pro:
```bash
pc start-pro
```



## Développeurs.ses

### Rebuild

Pour reconstruire l'image docker sans cache
```bash
pc rebuild-backend
```

### Restart

Pour effacer la base de données complétement, et relancer tous les containers:
```bash
pc restart-backend
```

### Reset

Si vos serveurs de dev tournent, et que vous souhaitez juste effacer les tables de la db:
```bash
pc reset-sandbox-db
```

Si vous voulez juste enlever les recommandations et bookings crées en dev par votre navigation:
```bash
pc reset-reco-db
```


### Migrate

Vous pouvez passer toutes les cli classiques d'alembic comme ceci:
```bash
pc alembic upgrade
```

### Test

Pour tester les apis du backend:
```bash
pc test-backend
```

Pour tester les apis du frontend:
```bash
pc test-frontend
```

Pour tester la navigation du site web
```bash
pc -e production test-cafe-webapp -b firefox
```

Exemple d'une commande test en dev sur chrome pour un fichier test particulier:
```bash
pc test-cafe-pro -b chrome:headless -f signup.js
```



## Deploy

### FRONTEND WEB

Pour déployer une nouvelle version web, par exemple en staging:
**(Attention de ne pas déployer sur la prod sans authorisation !)**
```bash
pc -t 8.0.0 tag-version-webapp
pc -e staging -t 8.0.0 deploy-frontend-webapp
```
Et pour pro sur staging, il suffit de remplacer la dernière commande par celle-ci:

```bash
pc -t 8.0.0 tag-version-pro
pc -e staging -t 8.0.0 deploy-frontend-pro
```

Lors du tag de version, vous devrez respecter le semantic versionning (https://semver.org/) : vN.x.0
N est le numéro de l'itération et x un autoincrément qui démarre à 0 et est changé en cas de hotfix en cours d'itération.

Pour déployer en production ensuite :

```bash
pc -e production -t 8.0.0 deploy-frontend-webapp
```

#### Publier shared sur npm

Pour publier une version de pass-culture-shared sur npm

```bash
cd shared
npm adduser
yarn version
yarn install
npm publish
```

Puis sur webapp et/ou pro, mettre à jour la version de pass-culture-shared dans le fichier `package.json` :

```bash
yarn add pass-culture-shared@x.x.x 
git add package.json yarn.lock
```

avec `x.x.x` nouvelle version déployée sur shared.


### BACKEND

Pour déployer une nouvelle version de l'API, par exemple en staging:
**(Attention de ne pas déployer sur la prod sans autorisation !)**

```bash
pc -t 8.0.0 tag-version-backend
pc -e staging -t 8.0.0 deploy-backend
```

Ensuite pour mettre en production le tag qui a été déployé sur l'environnement staging :

```bash
pc -e production -t 8.0.0 deploy-backend
```



## Administration

### Connexion à la base postgreSQL d'un environnement

Par exemple, pour l'environnement staging :

```bash
pc -e staging psql
```

### Connexion à en ligne de commande python à un environnement

Par exemple, pour l'environnement staging :

```bash
pc -e staging python
```

### Gestion des objects storage OVH

Pour toutes les commandes suivantes, vous devez disposer des secrets de connexion.


Pour lister le contenu d'un conteneur sépcific :

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

Vérifier déjà que l'un des admins (comme @arnoo) a enregistré votre adresse ip FIXE (comment savoir son adress ip? http://www.whatsmyip.org/)

#### Se connecter à la machine OVH

```bash
pc -e production ssh
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





## Version mobile (outdated, but can be useful someday)

### Emuler avec Cordova

```bash
yarn global add cordova-cli
```

```bash
cd webapp && cordova run ios
```

<!--
iPhone-5s, 11.2
iPhone-6, 11.2
iPhone-6-Plus, 11.2
iPhone-6s, 11.2
iPhone-6s-Plus, 11.2
iPhone-7, 11.2
iPhone-7-Plus, 11.2
iPhone-SE, 11.2
iPad-Air, 11.2
iPad-Air-2, 11.2
iPad--5th-generation-, 11.2
iPad-Pro--12-9-inch---2nd-generation-, 11.2
iPad-Pro--10-5-inch-, 11.2
Apple-TV-1080p, tvOS 11.2
Apple-TV-4K-4K, tvOS 11.2
Apple-TV-4K-1080p, tvOS 11.2
iPhone-8, 11.2
iPhone-8-Plus, 11.2
iPhone-X, 11.2
iPad-Pro--9-7-inch-, 11.2
iPad-Pro, 11.2
Apple-Watch-38mm, watchOS 4.2
Apple-Watch-42mm, watchOS 4.2
Apple-Watch-Series-2-38mm, watchOS 4.2
Apple-Watch-Series-2-42mm, watchOS 4.2
Apple-Watch-Series-3-38mm, watchOS 4.2
Apple-Watch-Series-3-42mm, watchOS 4.2
-->

### Développer en Android

Vous pouvez utiliser une ptite config ngrok pour l'api et la webapp par exemple:
```bash
cd webapp/ && yarn run ngrok
```

Ensuite il faut lancer l'application configurée avec ces tunnels:
```bash
pc start-browser-webapp -t
```

Vous pourrez alors utiliser l'url ngrok webapp pour dans votre navigateur android.

### Déployer le FRONTEND MOBILE

Pour déployer une nouvelle version phonegap (par default c'est en staging)
```bash
pc build-pg
```
