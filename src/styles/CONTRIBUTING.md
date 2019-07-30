# Styles

Nos règles de styles sont les suivantes:

## Outils externes

On utilise une librairie externe qui aide à définir des outils utilisés partout. Pour le moment on a [la-sass-vy](https://www.npmjs.com/package/la-sass-vy) qui apporte 3 utilités :

  - une règle mixin qui permet d'exprimer les fonts en pixel. On peut ainsi reprendre directement les valeurs px données dans les wireframes in vision, car la règle mixin convertit automatiquement en rem les tailles des fonts pour toutes les classes utilisant les sucres `.fs<px>`

  - des sucres syntaxiques `mb`, `my`, ... à la façon basscss, pour réduire la taille de code css, et rendre les fichiers css moins verbeux.

  - des classNames easy-handy pour définir des composants flex, ex : `flex-columns items-center justify-content` est la config souvent utilisée dans l'application pour faire des lignes flex d'objets.

## Règles dans les fichiers react pour appeler les classes

Au niveau des fichiers react avec des élèments portant des propriétés className, on applique le mieux possible le fait de :

  - ne pas mettre de `style={{}}` dans le react.

  - pour les components qui ont un style dependant du state, d'utiliser `className={classnames('class-name-constantes', { 'class-name-state-dependent' : state.isActivated })}`

  - ne pas utiliser les sucres syntaxique `mb`, `mt`, `py` directement dans react, mais les appeler en extend dans le scss. Donc par exemple si on a une fonction React:
    ```
      Foo = () => (<div className="foo"/>)
    ```
    On définit :
    ```
      .foo {
        @extend mb1;
        background-color:$red;
      }
    ```

## Structure du dossier

Tous les fichiers css sont placés dans ce dossier `src/styles`:

  - ce dossier a la même structure que `src/components` pour ranger ses fichiers.

  - chaque nom de fichier a un underscore `_machin.scss` et l’ensemble des fichiers sont importés dans un `index.scss` au même niveau.

  - `src/styles` a 4 sous-dossiers: variables, components, global, vendors


## Sous dossier `variables`

Les couleurs sont spécialement dans `src/styles/variables/_colors.scss` avec un code suffixe permettant d’avoir un ordre des intensités par couleur: lighter<light<rien<dark<darker

les z-index sont dans `src/styles/variables/_zindex.scss`

pour le moment, les autres variables sont dans `src/styles/variables/_guidelines.scss`


## Sous dossier `components`

Dans `src/styles/components`, chaque composant a son fichier de style. Par exemple pour un fichier `src/components/pages/Venue.jsx` défini par :

```
const Venue = ({ withFooter }) => (
  <main id="venue" className={classnames({ "with-footer": withFooter })} >
     <div className="controls" />
  </main>
)
```

on a un `src/styles/components/pages/_Venue.scss` qui encapsule les class des elements enfants et les class activables pour le même niveau que `#venue` de cette façon :

```
#venue {

 &.with-footer {
  @extend .fs32;
  @extend .mb2;
 }

 .controls {
  color: $blue;
 }
}
```


## Sous dossier `global`

Il comprend notamment:

  - un fichier `src/styles/global/_frame.scss` contient des règles pour les elements html: `*, body, html, h1` etc…

  - un autre ficher `src/styles/global/_helpers.scss` qui contient des classes utilisée en extend, avec souvent une syntaxe .is-machin
