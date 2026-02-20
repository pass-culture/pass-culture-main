# E2E

## Prérequis

Les tests E2E sont lancés sur l'app react en local (sur votre machine, et la CI). Il faut donc lancer l'app pro.
Il faudra aussi lancer pcapi, et vérifier qu'il n'y ait pas d'erreurs lors de l'execution des tests.

## Installation

```
npm install # Si vous ne l'avez pas encore fait
yarn playwright install # pour installer les browsers que playwright utilise
```

## Utilisation

Les tests e2e sont lancés via les commandes:

```
yarn test:e2e # pour le mode headed
yarn test:e2e:ci # pour le mode headless
yarn test:e2e:debug # pour faciliter le debug via les outils de playwright

```

Par défaut, les résultats sont dans le dossier `pro/test-results`.

## Structure
```
e2e/
├─ common/ # Contient les constantes et les assets utilisés par les tests
│  ├─ constants.ts
│  └─ data/
│     └─ librairie.jpeg
├─ fixtures/ # Contient la gestion des sessions pour les différents tests. Une fixture portera le même nom que le fichier de test.
│  ├─ common.ts # La fixture commune utilisée par les autres et gère la session. S'attends à appeler une méthode `callSandbox` qui crée les données nécessaires.
│  ├─ ....ts
├─ helpers/ # Différents helpers pour faciliter les tests
│  ├─ accessibility.ts
│  ├─ address.ts
│  ├─ assertions.ts
│  ├─ auth.ts
│  ├─ features.ts
│  ├─ requests.ts # Factorisation pour toutes les requêtes utilisées dans un page.waitForResponse
│  └─ sandbox.ts # Les différents appels à la sandbox existants.
```
## Problèmes connus

### PCAPI remonte des erreurs liés à des librairies.

Il faudra mettre à jour les dépendances côté api (Voir [la documentation](../../api/README.md#1-installation-des-dépendances)), puis redémarrer pcapi.


