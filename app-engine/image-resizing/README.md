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

Une nouvelle version est déployée si un changement est détecté dans ce micro service. 
Voir https://github.com/pass-culture/pass-culture-main/blob/2b8a2f52ec698bb64b06f9c495a65fdbf9a651b1/.github/workflows/dev_on_workflow_deploy_app_engine_image_resizing.yml#L1