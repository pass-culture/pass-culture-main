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
Les variables disponibles pour l'application sont décrites dans le fichier `src/config.js`

## Upgrade de la version

```bash
yarn version
# yarn version --new-version 0.2.1
```

## Icons Font (Fontello)

**Modifier les icones**

- Ouvrir [fontello.com](http://fontello.com) dans un navigateur
- Glisser/Déposer le fichier de configuration `public/static/fontello/config.json`

**Ajouter une nouvelle icone**

- Exporter l'icone depuis InVision
- Depuis un logiciel de dessin vectoriel:
  - Utiliser un plan de travail carré de 500px
  - Ajouter une shape carré transparent sans stroke de 500px en background
  - Transformer les strokes en shapes
  - Fusionner toutes les shapes
  - Exporter le fichier en `.svg`
  - Remplacer les `<rect>` dans le code svg par des `<g> | <path>`
- Nettoyer le fichier généré via [SVGMG](https://jakearchibald.github.io/svgomg/)
- Ouvrir [fontello.com](http://fontello.com) dans un navigateur
- Glisser/Déposer le fichier de configuration `./config.json`
- Ajouter la nouvelle icone par glisser/déposer
- Cliquer sur le bouton `Download`

**Importer les icones dans le projet**

- Dézipper le fichier téléchargé
- Extraire le contennu du fichier zip dans le dossier `public/static/`

## Animations entre les vues d'une même page

- Voir le fichier de la page profil `src/components/pages/ProfilePage`
- Les pages doivent avoir la classe CSS `transition-item`
- La page principale doit avoir la classe CSS `pc-page-view-main`
- La page fille doivent avoir la classe CSS `pc-page-view`

**Templates**

- ./.kiss/page-with-transition.js
