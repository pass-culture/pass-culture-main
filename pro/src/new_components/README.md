# Components (nouvelle archi)

## Description

Ce dossier contient tous les composants de niveau inferieur aux screens et supérieurs à ceux de l'UI-KIT.
Chacun d'entre eux représente une sous-fonctionalité qui est testable indépendament du reste.

Ces composants peuvent êtres réutilisables ou non, testés ou non, ajoutés à storybook ou non.

On préfèrera que ces composants soient le plus "bêtes" possibles, et éviter qu'il n'interragissent trop avec le monde exterieur (context, calls http, redux etc) et on préfèrera le passage de props tant que possible (tant que cela ne pénalise pas la lecture et la simplicité)

## Objectif

Découper les pages en sous-ensembles découplés et facilement apréhendable par un développeur, quelque soit son niveau d'experience ou sa conaissance du fonctionnel.

Optimiser la réutilisabilité du code

Réduire la taille des tests

## Stratégie de tests

En fonction de la nature du composant on délèguera les tests au `screen` qui fait appel à lui, ou non.

Pour en décider, plusieurs critères :

**Les tests du screen dont il dépend sont-ils déjà très complexes / long ?** et **le composant en question est-t-il complexe, et propose-t-il de nombreuses interactions / calculs ?**

Pour aléger et simplifier les tests du `screen`, on préfèrera alors déléguer une partie des tests au composant.
Il est possible d'exporter des `tests-utils` depuis le `component` vers le `screen` s'il est cohérent de partager de la logique :

Par exemple au sein d'un fichier `Components/MonComposant/test-utils/fillFormAndSubmit.tsx`, nous pourrions exporter une action complexe pour remplir un formulaire et le soumettre.
Cette action peut ainsi être utilisée à la fois dans le test du composant, mais aussi dans celui du `screen` dont il dépend.

## structure

```
/Components (new_components en atendant la migration)
+-- /MonComposant
|   +-- /__specs__                      // optional
|       +-- MonComposant.specs.tsx      // optional
|   +-- /__tests-utils__                // optional
|       +-- UneActionComplexeDeTest.tsx // optional
|       +-- UnMockPratique.tsx          // optional
|       +-- index.tsx                   // optional
|   +-- MonComposantSousComposant.tsx   // optional
|   +-- MonComposant.stories.tsx        // optional
|   +-- MonComposant.scss               // required
|   +-- MonComposant.tsx                // required
|   +-- index.ts                        // required
```

## Imports

on importera un `Component` ainsi :

```js
import MonComposant from '@components/MonComposant'
```

on accedera aux tests-utils ainsi :

```js
import {
  UneActionComplexeDeTest,
  UneAutreActionComplexeDeTest,
  UnMockPratique,
} from '@Components/MonComposant/tests-utils'
```

## Convention de nommage

La convention de nommage retenu pour les composants et leurs interface est la suivante:

```js
// prefix I pour interface
// prefix T pour types lorsqu'un type est necessaire
// suffix Props pour les interface des Props
interface IMonComposantProps {}

const MonComposant(props: IMonComposantProps): JSX.Element => {}
```


## DO

- nommer le composant principal comme le dossier
- exporter par defaut le composant principal depuis l'index
- si le composant est réutilisé dans plusieurs contextes : créer une story
- exporter depuis l'index tous les éléments publiques
- nommer les sous-composant en utilisant le nom principal comme préfixe
- ne jamais exporter un sous-composant depuis l'index (préférer extraire le sous-composant dans ce cas)
- pour regrouper des composants liés, préférer en général l'usage d'un prefix à la création d'un dossier
- regrouper les Screens liés entre eux alphabétiquement en utilisant un préfixe
    - `OfferCreation`
    - `OfferEdition`
    - `OfferEditionSuccess`
    - etc...

## Retour vers la doc

[Retour au README principal](../README.md)