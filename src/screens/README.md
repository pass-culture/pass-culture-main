# Screens

## Description

Ce dossier contiens tous les écrans. Un `screen` est le résultat d'une page une fois hydratée par les données du back-end à l'exclusion du layout général et des éléments récurents dans toutes les pages.

Un screen compose et orcherstre les éléments de la page (`components` et `ui-kit`).

## Objectif

Mettre à disposition une unité fonctionelle complete testable en isolation du state global et des appels faits au back-end.
Permettre de travailler dans storybook sans interférences.

## Stratégie de tests

Nous concentrons nos efforts de tests ici, puisque la plupart du fonctionnel y est implémenté.
Il est aussi possible d'exporter des actions depuis un dossier `tests-utils` à la fois utilisés localement et à vocation d'être ré-employé dans les tests des pages. 


## structure 

```
/Screens
+-- /MonScreen
|   +-- /__specs__                      // required
|       +-- MonScreen.specs.tsx         // required
|   +-- /__tests-utils__                // optional
|       +-- UneActionComplexeDeTest.tsx // optional
|       +-- UnMockPratique.tsx          // optional
|       +-- index.tsx                   // optional
|   +-- MonScreenSousComposant.tsx      // optional
|   +-- MonScreen.stories.tsx           // optional
|   +-- MonScreen.scss                  // required
|   +-- MonScreen.tsx                   // required
|   +-- index.ts                        // required
```

## imports 

on importera un `screen` ainsi : 

```js
import MonScreen from '@screens/MonScreen'
```

on accedera aux tests-utils ainsi : 

```js
import { 
  UneActionComplexeDeTest,
  UneAutreActionComplexeDeTest,
  UnMockPratique,
} from '@screens/MonScreen/tests-utils'
```

## DO
- nommer le screen principal comme le dossier
- exporter par defaut le screen principal depuis l'index
- créer une story pour le screen
- nommer les sous-composants en utilisant le nom principal comme préfixe

## Retour vers la doc

[Retour au README principal](../README.md)