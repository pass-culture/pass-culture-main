# pass-culture-browser

C'est la version (browser) de l'application frontend du Pass Culture.

Il faut aller voir le README dans https://github.com/betagouv/pass-culture-main
pour être informé des différentes lignes de commande associées à ce repo.

## Note sur Yarn

Yarn est prometteur, on vous conseille de l'utiliser. Tâchez de l'installer globalement sur votre ordinateur (https://yarnpkg.com/en/docs/install), puis:

```bash
yarn
```

## Upgrade de la version

```bash
yarn version
# yarn version --new-version 0.2.1
```

## Icons Font (Fontello)

**Ajouter une nouvelle icone**

- Exporter l'icone depuis InVision
- Depuis un logiciel de dessin vectoriel:
  - Utiliser un plan de travail carré de 500px
  - Ajouter une shape carré transparent sans stroke de 500px en background
  - Transformer les strokes en shapes
  - Fusionner toutes les shapes
  - Exporter le fichier en `.svg`
- Nettoyer le fichier généré via [SVGMG](https://jakearchibald.github.io/svgomg/)
- Ouvrir [fontello.com](http://fontello.com)
- Glisser/Déposer le fichier de configuration `./fontello.json`
- Ajouter le nouvelle icon par glisser/déposer
- Cliquer sur le bouton `Download`

**Importer les icones dans le projet**

- Dézipper le fichier téléchargé
- Renommer le dossier `fontello-<hash>` en `fontello`
- Couper/Coller le dossier dans `public/static/`
  