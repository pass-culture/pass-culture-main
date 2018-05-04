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

## Developer

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
    ./pc reset-backend-dev
  ```
  Si vous voulez juste enlever les recommandations et bookings crées en dev par votre
  navigation:
  ```bash
    ./pc reset-um-db
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
  Pour déployer une nouvelle version, par exemple en staging:
  (Attention de ne pas déployer sur la prod sans authorisation !)
  ```bash
    ./pc -e staging deploy-frontend
  ```

### FRONTEND MOBILE
  Pour déployer une nouvelle version (par default c'est en staging)
  ```bash
    ./pc build-pg
  ```

### BACKEND

#### CREDENTIALS

Vérifier déjà que l'un des admins (comme @arnoo) a
enregistré votre adresse ip FIXE (comment savoir son adress ip? http://www.whatsmyip.org/)

#### Manuellement
  Il faut se connecter à la machine
  ```
    ./pc -e staging ssh
  ```
  Et dans le terminal du server:
  ```
    screen -r
  ```
  Enfin dans le terminal du python flask, fait un contrôle d pour killer le process, puis:
  ```
    cd /home/deploy/pass-culture-main/ && ./pc restart-backend
  ```

#### Automatiquement (WIP)
  ```bash
    ./pc -e staging deploy-backend
  ```

#### Note pour une premiere configuration HTTPS (pour un premier build)

  Pour obtenir un certificat et le mettre dans le nginx (remplacer <domaine> par le domaine souhaité, qui doit pointer vers la machine hébergeant les docker)
  docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       certonly       --verb
  ose --webroot --webroot-path=/data/letsencrypt       -d <domaine>

  Puis mettre dans le crontab pour le renouvellement :

  0 0 * * * docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       renew       --verbose
  --webroot --webroot-path=/data/letsencrypt
