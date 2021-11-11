# Routes

## Description

Ce dossier contiens 2 types d'éléments, organisés en dossiers reproduisant au mieux la structure des URLS

### Les routeurs 

Comme leur nom l'indique, ils ont pour responsablitilé d'associer une page avec une route.

### Les composants de page 

Les composants ont pour responsabilité de charger toutes les données nécéssaires à l'affichage de la page, de structurer ces données puis d'hydrater le screen lié, tout en l'intégrant au layout général.
Si l'écran en question est un formulaire, la page à aussi la responsabilité de récupérer la donnée saisie, et de communiquer avec le serveur pour mener les opération. 


## Objectif

- gérer l'état pending/ready
- assurer la navigation générale.
- Mettre en forme les données en entrée et en sortie pour être consommés API => UI et UI => API.

## Stratégie de tests

Ici nous testons les I/O API => UI et UI => API
On peut importer des actions au sein des `tests-utils` des screen pour arriver au résultat nécéssaire.


## structure 

```
/Routes
+-- /MaRoute
|   +-- /__specs__                          // required
|       +-- MaRoute.specs.tsx               // required
|   +-- /__tests-utils__                    // optional
|       +-- UnMockPratique.tsx              // optional
|       +-- index.tsx                       // optional
|   +-- MaRoutePage.tsx                     // optional
|   +-- MaRoutePageFormaters.tsx            // optional
|   +-- MaRoute.stories.tsx                 // optional
|   +-- MaRoute.scss                        // required
|   +-- MaRoute.tsx                         // required
|   +-- index.ts                            // required
|   +-- /MaSousRoute
    |   +-- /__specs__                      // required
    |       +-- MaSousRoute.specs.tsx       // required
    |   +-- /__tests-utils__                // optional
    |       +-- UnMockPratique.tsx          // optional
    |       +-- index.tsx                   // optional
    |   +-- MaSousRoutePage1.tsx            // optional
    |   +-- MaSousRoutePage1Formaters.ts    // optional
    |   +-- MaSousRoutePage2.tsx            // optional
    |   +-- MaSousRoutePage2Formaters.ts    // optional
    |   +-- MaSousRoute.stories.tsx         // optional
    |   +-- MaSousRoute.scss                // required
    |   +-- MaSousRoute.tsx                 // required
    |   +-- index.ts                        // required
```

## DO

- Reproduire la structure de l'URL en utilisant la structure des dossiers
- Créer des `formaters` pour traiter la donnée avant d'hydrater les pages, ou de la retourner aux APIs
- N'afficher l'écran qu'une fois la page hydratée
- Si votre page est très complexe (beaucoup de composants imbriqués), afin de diminuer le nombre de passage de props à travers les composants, il est possible de faire usage d'un contexte pour faire passer les données et méthodes nécéssaires.

## Retour vers la doc

[Retour au README principal](../README.md)