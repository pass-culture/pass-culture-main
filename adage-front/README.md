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

1. Générer le token sur [le site de JWT](https://jwt.io) avec la config suivante:

- Header:

```
{
  "alg": "RS256",
  "typ": "JWT"
}
```

- PAYLOAD:

```
{
  "sub": "1234567890",
  "name": "<your_name>",
  "admin": true,
  "exp": 1516239022000
  "mail": "<your_email>"
}
```

2. Coller la public key qui se trouve le cadre `Verify signature` dans `api/src/pcapi/routes/adage_iframe/public_key/public_key.development` (remplacer l'existante)

3. Copier le token et le rajouter en query param dans l'url: `http://localhost:3002/?token=<votre_token>`

## Affichage d'offres en local

Comme le local est branché sur algolia de testing, les ids qui sont remontés d'algolia sont ceux de testing, et il n'est pas certain qu'on ait les mêmes en local.

Pour récupérer les ids de certaines offres en local, on peut soit

- faire une requête dans la bdd locale de type `select id from offer where "isEducational" = true;`

- récupérer les ids humanizés dans l'url des offres depuis PRO et les déshumaniser en utilisant [ce petit helper](https://jyq58.csb.app/)

- Editer `adage-front/src/app/components/OffersInstantSearch/OffersSearch/Offers/Offers.tsx` en remplaçant `hits` par un tableau d'identifiants:

```
const queries = useQueries(
   hits.map(hit => ({
   }))
 )
```

devient

```
const queries = useQueries(
   [<id1>, <id2>, <id3>].map(hit => ({
   }))
 )
```
