# pass-culture-main

C'est tout le framework du Pass Culture!

## Minimal Process

### Install
  Il vous faudra une machine UNIX.

  Installer docker (https://docs.docker.com/install/) et docker-compose (https://docs.docker.com/compose/install/#install-compose)

  Installer yarn (voir le README dans le dépot pass-culture-webapp), puis:

  ```bash
    ./pc install
  ```

### Init
  Pour obtenir une base de données minimale.
  ```bash
    ./pc set-backend-dev
  ```

### Démarrage
  Pour lancer l'API:
  ```bash
    ./pc start-backend
  ```
  Pour lancer l'appli Web:
  ```bash
    ./pc start-frontend
  ```
  avec le dexie worker
  ```bash
    ./export HAS_WORKERS=true && pc start-frontend
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
  Si vos serveurs de dev tournent, et que vous souhaitez juste effacer
  les tables de la db:
  ```bash
    ./pc reset-sandbox-db
  ```
  Si vous voulez juste enlever les recommandations et bookings crées en dev par votre
  navigation:
  ```bash
    ./pc reset-reco-db
  ```

### Migrate
  Vous pouvez passer toutes les cli classiques d'alembic
  comme ceci:
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
    ./pc -e production testcafe -b firefox
  ```

### Emuler avec Cordova

```bash
  yarn global add cordova-cli
```

```bash
  cd webapp && cordova run ios
```
<!-- iPhone-5s, 11.2
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
Apple-Watch-Series-3-42mm, watchOS 4.2 -->

### Développer en Android

  Vous pouvez utiliser une ptite config ngrok pour l'api et la webapp par exemple:
  ```
    cd webapp/ && yarn run ngrok
  ```
  Ensuite il faut lancer l'application configurée avec ces tunnels:
  ```
    ./pc start-browser-webapp -t
  ```
  Vous pourrez alors utiliser l'url ngrok webapp pour dans votre navigateur android.


## Deploy

### FRONTEND WEB
  Pour déployer une nouvelle version web, par exemple en staging:
  (Attention de ne pas déployer sur la prod sans authorisation !)
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

Vérifier déjà que l'un des admins (comme @arnoo) a
enregistré votre adresse ip FIXE (comment savoir son adress ip? http://www.whatsmyip.org/)

#### Se connecter à la machine
  ```
    ./pc -e staging ssh
  ```

#### Accéder aux runs
  Une fois connecté:
  ```
    screen -ls
  ```
  Pour savoir le screen où se passe le serveur. Et alors:
  ```
    screen -r <id session>
  ```
  Dans ce screen, vous pouvez faire un contrôle d pour killer le process, puis
  n'importe quelle commande pc pour relancer les processes.

#### Updater le code
  Une fois connecté:
  ```
    cd /home/deploy/pass-culture-main/ && ./pc update-code
  ```

#### Updater la db
  Une fois connecté:
  ```
    cd /home/deploy/pass-culture-main/ && ./pc update-db
  ```

#### Note pour une premiere configuration HTTPS (pour un premier build)

  Pour obtenir un certificat et le mettre dans le nginx (remplacer <domaine> par le domaine souhaité, qui doit pointer vers la machine hébergeant les docker)
  docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       certonly       --verb
  ose --webroot --webroot-path=/data/letsencrypt       -d <domaine>

  Puis mettre dans le crontab pour le renouvellement :

  0 0 * * * docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       renew       --verbose
  --webroot --webroot-path=/data/letsencrypt
