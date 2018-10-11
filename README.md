# pass-culture-browser

C'est la version (browser) de l'application frontend du Pass Culture.

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

## Upgrade de la version

```bash
yarn version
# yarn version --new-version 0.2.1
```

## Update de la font icon

- Ouvrir le site [Fontello.com](https://fontello.com)
- Glisser/Déposer le fichier `public/static/fontello/config.json` dans la page du navigateur
- Ajouter une/des icônes
- Cliquer sur `Download webfont (n)`
- Remplacer et committer le fichier `public/static/fontello/config.json`
