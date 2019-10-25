# API SWAGGER DOCUMENTATION

## Pré-requis

- Nous utilisons le plugin Flasgger(https://github.com/rochacbruno/flasgger) permettant de visualiser via une app Flask, les specifications écrites dans un fichier .json


# Visualiser la documentation

Lancer le serveur : `python api_doc.py`

L'application est visible sur http://localhost:5000/documentation/swagger/


# Tester les routes en local

Lancer le serveur `pc start-backend`
Créer des données avec `pc sandbox -n industrial`

roberto.mamarx@momarx.io | user@AZERTY123 | offererId : 9 | ApiKey : "NA5Q2A6YA4LUJ9FEMET4QM4QB4QMJYCQAQ5MSMTUP9QQTMGEV9SA4AUYKMKY7USA"

- Réponse 200
Utiliser l'api key "NA5Q2A6YA4LUJ9FEMET4QM4QB4QMJYCQAQ5MSMTUP9QQTMGEV9SA4AUYKMKY7USA" et le token 100003

- Réponse 410
100005 : "Cette réservation a déjà été validée"

- Réponse 403
100002 (Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l'évènement)

## Comment écrire ajouter une nouvelle route ?

- Nous utilisons le standard https://swagger.io/docs/specification/2-0/basic-structure/

- Nous suivons la sec OpenAPI 2 en attendant une mise à jour de flasgger
 https://github.com/OAI/OpenAPI-Specification/

- Un example
https://github.com/flasgger/flasgger/blob/master/examples/example_app.py
