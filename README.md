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
    ./pc update_providables -m
    ./pc init
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
    ./pc reset-all-db
  ```
  If you
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
    ./pc testcafe -b firefox -e production
  ```

## Deploy

### HTTPS first configuration
  Pour obtenir un certificat et le mettre dans le nginx (remplacer <domaine> par le domaine souhaité, qui doit pointer vers la machine hébergeant les docker)
  docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       certonly       --verb
  ose --webroot --webroot-path=/data/letsencrypt       -d <domaine>

  Puis mettre dans le crontab pour le renouvellement :

  0 0 * * * docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       renew       --verbose
  --webroot --webroot-path=/data/letsencrypt

### Push
  Pour déployer une nouvelle version:
  (Attention de ne pas déployer sur la prod sans authorisation !)
  ```bash
    ./pc rebuild-frontend
    ./pc deploy-frontend
  ```

  ```bash
    ./pc deploy-backend
  ```
