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
./pc install
```
Le script `pc` sera automatiquement lié dans votre dossier `/usr/local/bin`

### Init
Pour verifier les tests et obtenir une db minimale:
```bash
./pc test-backend
```

### Démarrage

Pour lancer l'API:
```bash
./pc start-backend
```

Pour lancer l'appli Web:
```bash
./pc start-webapp
```

Pour lancer le portail pro:
```bash
./pc start-pro
```



## Développeurs.ses

### Rebuild

Pour reconstruire l'image docker sans cache
```bash
./pc rebuild-backend
```

### Restart

Pour effacer la base de données complétement, et relancer tous les containers:
```bash
./pc restart-backend
```

### Reset

Si vos serveurs de dev tournent, et que vous souhaitez juste effacer les tables de la db:
```bash
./pc reset-sandbox-db
```

Si vous voulez juste enlever les recommandations et bookings crées en dev par votre navigation:
```bash
./pc reset-reco-db
```

### Dump Prod To Staging

ssh to the prod server
```bash
cd ~/pass-culture-main && ./pc dump-prod-db-to-staging
```

Then connect to the staging server:
```bash
cd ~/pass-culture-main
cat "../dumps_prod/2018_<TBD>_<TBD>.pgdump" docker exec -i docker ps | grep postgres | cut -d" " -f 1 pg_restore -d pass_culture -U pass_culture -c -vvvv
./pc update-db
./pc sandbox
```

### Migrate

Vous pouvez passer toutes les cli classiques d'alembic comme ceci:
```bash
./pc alembic upgrade
```

### Test

Pour tester les apis du backend:
```bash
./pc test-backend
```

Pour tester les apis du frontend:
```bash
./pc test-frontend
```

Pour tester la navigation du site web
```bash
./pc -e production test-cafe-webapp -b firefox
```

Exemple d'une commande test en dev sur chrome pour un fichier test particulier:
```bash
./pc test-cafe-pro -b chrome:headless -f signup.js
```

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
./pc start-browser-webapp -t
```

Vous pourrez alors utiliser l'url ngrok webapp pour dans votre navigateur android.


## Deploy

Le deploy passe par Netligy<br>
Il est obligatoire d'installer le module [netlify](https://www.npmjs.com/package/netlify)

```bash
npm i -g netlify
```


### FRONTEND WEB

Pour déployer une nouvelle version web, par exemple en staging:
**(Attention de ne pas déployer sur la prod sans authorisation !)**
```bash
./pc -e staging deploy-frontend
```

### FRONTEND MOBILE

Pour déployer une nouvelle version phonegap (par default c'est en staging)
```bash
./pc build-pg
```

### BACKEND

#### CREDENTIALS

Vérifier déjà que l'un des admins (comme @arnoo) a enregistré votre adresse ip FIXE (comment savoir son adress ip? http://www.whatsmyip.org/)

#### Se connecter à la machine

```bash
./pc -e staging ssh
```

#### Accéder aux runs

Une fois connecté:

```bash
screen -ls
```

Pour savoir le screen où se passe le serveur. Et alors:
```bash
screen -r <id session>
```

Dans ce screen, vous pouvez faire un contrôle d pour killer le process, puis n'importe quelle commande pc pour relancer les processes.

#### Updater le code

Une fois connecté:
```bash
cd /home/deploy/pass-culture-main/ && pc update-code
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
