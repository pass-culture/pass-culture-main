# E2E

## Prérequis

Les tests E2E sont lancés sur l'app react en local (sur votre machine, et la CI). Il faut donc lancer l'app pro.
Il faudra aussi lancer pcapi, et vérifier qu'il n'y ait pas d'erreurs lors de l'execution des tests.

### Clé d'API E2E (`E2E_API_KEY`)

Les routes internes de seeding de l'API (`/sandboxes/...`, `/e2e/...`, `/testing/...`) sont protégées par un header `x-api-key`. Les tests Playwright envoient ce header en lisant `process.env.E2E_API_KEY`.

Il faut donc définir la **même valeur** des deux côtés, dans deux fichiers `.env.local.secret` (tous deux sont gitignorés) :

- `api/.env.local.secret` : `E2E_API_KEY="dummysecret"`
- `pro/.env.local.secret` : `E2E_API_KEY="dummysecret"`

NB: Les tests e2e écrasent et recréent les données dans postgres. Pour éviter d'utiliser votre postrge de développement, vous pouvez ajouter la variable d'environnement `IS_E2E_TESTS=1` dans l'api.
Par exemple, si vous lancez l'api dans docker, vous pouvez ajouter dans le `docker-compose-backend.yml` :

```yml
  flask:
    ...
    environment:
      - IS_E2E_TESTS=1
    ...
```

## Installation

```
pnpm install # Si vous ne l'avez pas encore fait
pnpm playwright install # pour installer les browsers que playwright utilise
```

## Utilisation

Les tests e2e sont lancés via les commandes:

```
pnpm test:e2e # pour le mode headed
pnpm test:e2e:ci # pour le mode headless
pnpm test:e2e:debug # pour faciliter le debug via les outils de playwright

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

## Conventions d'écriture

### Sélecteurs : Sensibilité à la casse et match d'une chaîne de caractère complète

Contrairement à **Testing Library**, les locators **Playwright** ne sont **pas sensibles à la casse** et **ne matchent pas la chaîne de caractère complète** par défaut (cf [la doc](https://playwright.dev/docs/api/class-page#page-get-by-text-option-exact))

* **Par défaut :** `page.getByRole('heading', { name: 'offres' })` validera un titre affichant **"Offres réservables"**.
* **Mode strict :** Pour forcer le respect de la casse et le match sur la chaîne de caractère complète, utilisez `{ exact: true }`.

**Note :** Nous avons choisi de ne pas imposer `exact: true` systématiquement pour préserver la lisibilité, mais restez vigilants si un test passe alors que la casse ne correspond pas.


## Problèmes connus

### PCAPI remonte des erreurs liés à des librairies.

Il faudra mettre à jour les dépendances côté api (Voir [la documentation](../../api/README.md#1-installation-des-dépendances)), puis redémarrer pcapi.
