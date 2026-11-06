# Design System du pass Culture

Ce _repository_ contient le code nécessaire à la génération des _design tokens_ du Design System du pass Culture. Si vous cherchez des informations plus générales à propos de ce design system, rendez-vous sur [la documentation](https://zeroheight.com/6b27136ed).

Si vous êtes développeur·euse ou designer·euse, et que vous voulez utiliser le Design System du pass Culture, vous pouvez commencer avec les [kits de démarrage](https://zeroheight.com/6b27136ed/p/02dbf9-kit-de-demarrage).

## Installation et utilisation

La dernière version de la librairie peut être installée dans un projet avec la commande suivante :

```bash

yarn add @pass-culture/design-system

```

La librairie donne accès aux _design tokens_ soit via un fichier de variables CSS qu'on peut importer cette manière :

```css
@import '@pass-culture/design-system/lib/pro/light.css';
```

Dans ce cas, les variables CSS sont directement déclarées à la racine de l'arbre du document.

Ou bien via un fichier typescript depuis lequel on importe l'objet contenant les _design tokens_ :

```js
import * as tokens from '@pass-culture/design-system/lib/jeune/light.web.ts'
```

## Création d'une nouvelle version de la librairie

1. Créer un nouveau tag via le workflow manuel ["Update package version and create tag"](https://github.com/pass-culture/design-system/actions/workflows/create_tag.yml)

2. Publier [une nouvelle _release_ Github](https://github.com/pass-culture/design-system/releases/new) avec le détail des changements basée sur le tag créé à l'étape précédente

3. Vérifier que la publication du package a eu lieu à l'issue de l'[action de publication](https://github.com/pass-culture/design-system/actions)

## Fonctionnement du build

Le but du _build_ est de transformer l'objet JSON contenant les _design tokens_ exportés depuis Figma en des fichiers exploitables par les applications du pass Culture (les fichiers `light.web.css` ou `dark.web.ts` donnés en exemple plus haut).

### Transformation des design tokens

On utilise la librairie [style-dictionary](https://github.com/amzn/style-dictionary) qui nous permet de configurer des _pipelines_ qui appliquent des transformations spécifiques pour chaque environnement de destination.

Ces fichiers de configuration se trouvent dans `src/configs` et permettent de construire pour chaque _brand_ les fichiers de variables déclinés pour chaque plateforme et pour chaque thème concernés.

### Autres fichiers générés

On génère aussi deux autres fichiers :

- Le fichier `font-faces.css` contenant les définitions des typographies utilisées dans les _design tokens_
- Le fichier `font-preloads.ts` contenant la liste des _preloads_ à injecter dans le HTML des applications pour que les glyphes des typographies soient téléchargés en premier

## Structure des design tokens

Les _design tokens_ sont séparés en trois catégories :

- Les _global tokens_, c'est à dire les valeurs par défaut des tokens
- Les _tokens_ de thèmes qui surchargent les valeurs par défaut au moment du _build_
- Les _brand tokens_ qui surchargent les _tokens_ pour une _brand_ et un thème donnés

### Global tokens

Les _global tokens_ sont organisés par groupe. On a par exmeple `typography` ou `color`. Chacun de ces groupes est divisé en plusieurs fichiers :

- Les _primitive tokens_ qui font référence à des valeurs absolues (par ex: `color-grey-0: "#fff"`)
- Les _semantic tokens_ qui sont des abstractions des _primitive tokens_. Ils peuvent être lié à un style partagé par les applications (par ex: `color-text-default`), ou a un composant spécifique (par ex: `button-color-background-default-hover`)

### Theme tokens

Les _theme tokens_ sont regroupés dans des fichiers spécifiques pour chaque thème possible sur les différentes plateformes (tel que `dark.json` pour le thème sombre).

### Brand tokens

Les _brand tokens_ sont regroupés dans des fichiers spécifiques pour chaque plateforme et chaque thème possible (tel que `pro-dark.json` pour la surcharge du thème sombre sur l'application pro).

### Output mobile (React Native)

Les fichiers `lib/<brand>/<theme>.mobile.ts` sont destinés à React Native. Pour la brand `jeune`, les tokens typography en *Italic* sont exportés avec `fontFamily: "Montserrat"` + `fontWeight` + `fontStyle: "italic"` afin d'assurer le rendu iOS. Les outputs web ne sont pas modifiés.

### Comment ajouter une brand ?

- Ajouter à `src/configs/brands` une config de plateformes et de thèmes pour la nouvelle brand
- Ajouter un fichier de surcharge pour chaque thème dans `src/tokens/brands` sous la forme `[BRAND]-[THEME].json`

### Comment ajouter un thème ?

- Ajouter le thème aux listes des thèmes dans les configs de brand concernées dans `src/configs/brands`
- Ajouter un fichier de surcharge pour chaque brand dans `src/tokens/brands` sous la forme `[BRAND]-[THEME].json`
