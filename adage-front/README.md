# pass-culture-adage-front

[![Coverage Status](https://coveralls.io/repos/github/pass-culture/pass-culture-adage-front/badge.svg?branch=master)](https://coveralls.io/github/pass-culture/pass-culture-adage-front?branch=master)

Application web pour les rédacteurs de projets scolaires, leur permettant de réserver des offres sur le pass Culture pour leurs élèves.

Il faut aller voir le README dans https://github.com/betagouv/pass-culture-main pour être informé des différentes lignes de commande associées à ce repo.

## Note sur Yarn

Yarn est prometteur, on vous conseille de l'utiliser. Tâchez de l'installer globalement sur votre ordinateur (https://yarnpkg.com/en/docs/install), puis:

```bash
  yarn
```

## Installation et Lancement de l'application

- ```shell
  yarn install
  yarn start
  ```

## Lancement des tests

- ### Lancement des tests unitaires
  ```shell
  yarn test:unit
  ```

## Installation d'un token pour accéder à l'application en local

1. Ouvrir la console bash

```bash
$ pc bash
```

2. Générer un token via la commande

```bash
flask generate_fake_adage_token
```

3. Copier l'url générée dans le navigateur pour accéder à l'app

## Affichage d'offres en local

Comme le local est branché sur algolia de testing, les ids qui sont remontés d'algolia sont ceux de testing, et il n'est pas certain qu'on ait les mêmes en local.

Pour récupérer les ids de certaines offres en local, on peut utiliser un index local. Pour cela, il faut :

- Créer un nouvel index sur la sandbox algolia : `<votre_nom>-collective-offers`

- Créer un fichier `.env.development.local` dans le dossier `adage-front` et renseigner le nom de l'index dans la variable `REACT_APP_ALGOLIA_COLLECTIVE_OFFERS_INDEX`

- Créer un fichier `.env.local.secret`

```
ALGOLIA_COLLECTIVE_OFFERS_INDEX_NAME=<votre_nom>-collective-offers
ALGOLIA_TRIGGER_INDEXATION=1
ALGOLIA_API_KEY=<demander l'api key>
ALGOLIA_APPLICATION_ID=testingHXXTDUE7H0
SEARCH_BACKEND=pcapi.core.search.backends.algolia.AlgoliaBackend
```

- Ouvrir la console bash

```
$ pc bash
```

- Réindexer vos offres collectives

```
flask reindex_all_collective_offers
```
