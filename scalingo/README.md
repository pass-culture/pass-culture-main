# Scalingo deploy

Première étape, installer la cli scalingo :

curl -O https://cli-dl.scalingo.io/install && bash install


Ajouter votre clé ssh pour effectuer les opérations sur scalingo depuis votre terminal :

`scalingo keys-add [KEY_NAME] [PUBLIC_KEY]`

Si vous souhaitez créer une nouvelle clé :

`ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`


## Création d'un nouvel environnement sur Scalingo :

Utiliser le script init_new_project.sh
Example d'appel : pour créer un projet à l'URL api.passculture-dev.beta.gouv.fr avec une base de donnée postgresql de type 1g 
(https://scalingo.com/databases/postgresql) et 2 instances de backend.
La commande déploiera la branche locale de votre dépôt Github.

`./init_new_project.sh -n pass-culture-api-dev -r dev -d 1g -b 2 -u api.passculture-dev.beta.gouv.fr`

## Restauration d'un backup sur l'un des environnements Scalingo

Première étape, installer les paquets clients de postgresql :

`apt install postgresql-client-9.5`

(Les autres versions postgresql-client > 9.5 devraient fonctionner)

WIP: script restore_backup.sh