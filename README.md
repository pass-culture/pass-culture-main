# pass-culture-main

C'est tout le framework du Pass Culture!

## Minimal Process

### Install
  Check the README in webapp to make sure you have yarn.
  Then
  ```bash
    ./pc install
  ```

  Pour obtenir un certificat et le mettre dans le nginx (remplacer <domaine> par le domaine souhaité, qui doit pointer vers la machine hébergeant les docker)
  docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       certonly       --verb
ose --webroot --webroot-path=/data/letsencrypt       -d <domaine>

  Puis mettre dans le crontab pour le renouvellement :

  0 0 * * * docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt       -v ~/pass-culture-main/certs-data:/data/letsencrypt       deliverous/certbot       renew       --verbose
 --webroot --webroot-path=/data/letsencrypt

### Init
  It will set a minimal database:
  ```bash
    ./pc init
  ```

### Start
  Make the flask, postgres and nginx working:
  ```bash
    ./pc start-backend
  ```
  Make the webapp:
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
