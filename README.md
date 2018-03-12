# pass-culture-main

C'est tout le framework du Pass Culture!

## Minimal Process

### Install
  Il vous faudra une machine UNIX.
  
  Installer docker (https://docs.docker.com/install/) et docker-compose (https://docs.docker.com/compose/install/#install-compose)

  Installer yarn (voir le README dans le dépot pass-culture-webapp)
  Then
  ```bash
    ./pc install
  ```

  Pour obtenir un certificat et le mettre dans le nginx (remplacer <domaine> par le domaine souhaité, qui doit pointer vers la machine hébergeant les docker)
  docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       certonly       --verb
ose --webroot --webroot-path=/data/letsencrypt       -d <domaine>

  Puis mettre dans /etc/crontab pour le renouvellement :

  0 0 * * * docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       renew       --verbose
 --webroot --webroot-path=/data/letsencrypt

### Init
  Pour obtenir une base de données minimale.
  ```bash
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
  When you feel that all the backend is broken/unsynchronized, niginx config changing...
  ```bash
    ./pc rebuild-backend
  ```

### Restart
  When you feel that the database needs to be completely deleted and completely reset so as the flask reinstanciates:
  ```bash
    ./pc restart-backend
  ```

### Reset
  When all is running and you need just to wash/clear peacefully
  all your db and maybe feed it by something else:
  It will reset the database:
  ```bash
    ./pc reset-db
  ```

### Migrate
  We use alembic, so just pass al the classic alembic options after a ./pc alembic cli, like
  ```bash
    ./pc alembic upgrade
  ```

### Test
  Using pytest and hypothesis for testing backend apis:
  ```bash
    ./pc test-backend
  ```

  Using jest to do unit testing on frontend javascript functions:
  ```bash
    ./pc test-frontend
  ```

  Using testcafe for testing browser navigation of the app (default is on the development chrome brower)
  ```bash
    ./pc testcafe -b firefox -e production
  ```

## Deploy
  When you need to update a new version of the app
  (Please be careful to not deploy in prod without authorization !)
  ```bash
    ./pc rebuild-frontend
    ./pc deploy-frontend
  ```

  ```bash
    ./pc deploy-backend
  ```
