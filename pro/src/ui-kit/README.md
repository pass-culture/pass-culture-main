# Ui-kit

## Description

On y trouvera notament :

- éléments typographiques
- éléments de formulaire
- boutons
- jeux d’icônes
- grilles de mise ne page
- etc...

## Objectif

Créér un ensemble d'outils de mise en page standardisés, hautement réutilisables et leur donner de la visibilité à travers le styleguide (storybook). Maximiser la réutilisabilité de ces éléments. Faciliter la communication avec le design en ce qui concerne la charte graphique.

## Stratégie de tests

Dans la plupart des cas, on évitera de créer des tests pour ces éléments, car leur comportement sera déjà testé à travers des tests de plus haut niveau.

## structure

```
/Ui-kit
+-- index.ts                            // required (exporte tous les éléments)
+-- /MonComposant
|   +-- /__specs__                      // avoid if possible
|       +-- MonComposant.specs.tsx      // avoid if possible
|   +-- /__tests-utils__                // avoid if possible
|       +-- UneActionComplexeDeTest.tsx // avoid if possible
|       +-- UnMockPratique.tsx          // avoid if possible
|       +-- index.tsx                   // avoid if possible
|   +-- MonComposantSousComposant.tsx   // optional
|   +-- MonComposant.stories.tsx        // required
|   +-- MonComposant.scss               // required
|   +-- MonComposant.tsx                // required
|   +-- index.ts                        // required

```

## Imports

on importera les éléments de l'`ui-kit` ainsi :

```js
import { Heading1, Heading2, Grid, InputText } from 'ui-kit'
```

## DO

- toujours prévoir une prop pour l’ajout d’une classe sur le wrapper de l’élément
- nommer l’élément d'`ui-kit` principal comme le dossier
- exporter par defaut le l’élément d'`ui-kit` principal depuis l’index
- créer une story pour l’élément d'`ui-kit`
- nommer les sous-composant en utilisant le nom principal comme préfixe
- exporter aussi l’élément depuis l’index du dossier principal (il y aura généralement beaucoup d’imports depuis l'`ui-kit`)

## DON'T

- ne pas définir de marges extèrieures sur le wrapper
- ne pas surcharger les styles de l’élément depuis un composant de plus haut niveau
- ne pas faire appel à des styles globaux (autre que mixins, variables et fonctions)
- l’élément ne peut avoir que 3 types de tailles:
  - fixes ex: une icône (32px)
  - naturelle ex: un boutton (en fonction de la longueur du texte)
  - flexible (100% / block / flex)

## Retour vers la doc

[Retour au README principal](../README.md)
