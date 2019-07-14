# pass-culture-browser

[![Coverage Status](https://coveralls.io/repos/github/betagouv/pass-culture-browser/badge.svg?branch=master)](https://coveralls.io/github/betagouv/pass-culture-browser?branch=master)

C'est la version (browser) de l'application frontend du pass Culture.

Il faut aller voir le README dans https://github.com/betagouv/pass-culture-main
pour être informé des différentes lignes de commande associées à ce repo.

## Note sur Yarn

Yarn est prometteur, on vous conseille de l'utiliser. Tâchez de l'installer globalement sur votre ordinateur (https://yarnpkg.com/en/docs/install), puis:

```bash
yarn
```

## Variables d'environnements

A la racine de webapp créer un fichier `env.local`<br>
Les variables disponibles pour l'application sont décrites dans le fichier `src/utils/config.js`

## Tests

#### Tests Unitaires (Jest/Enzyme)

Lancer tous les tests
```bash
yarn test:unit
# Lancer les tests unitaires en local en mode rafraichissement auto
# yarn test:unit --watchAll
```

Lancer un seul fichier en mode watch
```bash
./node_modules/.bin/jest --env=jsdom ./<path>/tests/<fichier> --watch
# yarn test:unit ./path/to/file.spec.js --watch
```

#### Tests Fonctionnels/E2E (Testcafe)

Lancer tous les tests
```bash
pc reset-all-db
pc sandbox --name=industrial
yarn test:cafe
```

Lancer un seul fichier en ligne de commande depuis un environnement local
```bash
./node_modules/.bin/testcafe chrome ./testcafe/02_signin.js
```

## Upgrade de la version

La commande `yarn version` va créée un nouveau commit de version, un nouveau tag et la version sera mise à jour sur la page Mentions Légales
```bash
yarn version
# yarn version --new-version x.x.x
```

## Font Icons (Fontello)

#### Ajout d'icones

- Ouvrir le site [Fontello.com](https://fontello.com)
- Glisser/Déposer le fichier `public/static/fontello/config.json` dans la page du navigateur
- Ajouter une/des icônes
- Cliquer sur `Download webfont (n)`
- Remplacer et committer le fichier `public/static/fontello/config.json`

#### Mise à jour

La commande ci-dessous permet de mettre à jour le dossier dans `public/static/fontello` avec la dernière configuration à jour
```bash
yarn fontello
```

[Nous Contacter](https://docs.passculture.app/experimentateurs)
