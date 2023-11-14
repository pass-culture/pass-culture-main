# image-resizing

Cette application est déployé grâce à GCP App Engine.
Elle permet à l'application native d'obtenir des images redimensionnées en les requêtant aux buckets GCP.

## Installation et lancement

L'application n'a pour l'instant été testée qu'avec Python 3.9.

```shell
$ python3.9 -m pip install -r requirements.txt
$ python3.9 -m flask --app main:app run
```

## Déploiement

La version de cette application est contenue dans le fichier `version.txt`.
Pour qu'une nouvelle version soit déployée, il faut augmenter manuellement le numéro de version dans ce fichier.