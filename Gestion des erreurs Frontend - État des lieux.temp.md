# Gestion des erreurs Frontend — État des lieux

> [!NOTE]
> Ce document a été construit et rédigé avec l'assistance de l'IA.

## Vue d'ensemble

Le Frontend Pro dispose d'un système de gestion des erreurs **multi-couches** mais **hétérogène**. L'infrastructure de base est solide (intercepteurs HTTP, classes d'erreur typées, intégration Sentry), mais les conventions d'usage varient fortement d'un composant à l'autre.

Ce document compare **l'état actuel du codebase** à **l'état cible** défini dans `Gestion des erreurs Frontend - RFC` (le document de référence de ce chantier). Chaque écart identifié ici correspond à une **case à combler**, qui sera ensuite :

1. Traduite en une ou plusieurs solutions dans `Gestion des erreurs Frontend - Propositions techniques` (document de travail temporaire).
2. Adressée par un ticket dans `Gestion des erreurs Frontend - Tickets JIRA`.

---

## Ce qui fonctionne bien

### Intercepteurs HTTP globaux

Les erreurs critiques sont interceptées au niveau du `fetch` custom (`clientConfig.ts`, `clientConfigAdage.ts`) :

- **401 Unauthorized** → déconnexion automatique (sauf whitelist : `/users/current`, `/offerers/names`, `/users/signin`)
- **503 Service Unavailable** → redirection vers la page de maintenance

Ces intercepteurs fonctionnent de manière transparente pour tout le code appelant. **Aligné avec la RFC.**

### Classe `ApiError` et type guards

Une classe `ApiError` uniforme (`status`, `body`, `url`, `statusText`) est produite par l'intercepteur d'erreur enregistré dans `apiClient/api.ts`. Les type guards `isErrorAPIError()` et `hasErrorCode()` sont utilisés de façon cohérente dans le codebase. **Aligné avec la RFC.**

### Intégration Sentry

Trois niveaux de reporting :

- `handleError()` — erreurs attendues (snackbar + Sentry + console)
- `handleUnexpectedError()` — erreurs inattendues (contexte Sentry enrichi, snackbar optionnel)
- `sendSentryCustomError()` — erreurs spécifiques avec tags et breadcrumbs

### Page 404

La page 404 (`pages/Errors/NotFound/NotFound.tsx`) existe. Avec les décisions de la RFC, son usage doit être **restreint aux routes inexistantes** (non résolvables par le router). Les erreurs de chargement de données sur une route existante ne doivent plus y rediriger — ce comportement est aujourd'hui en place dans le handler SWR global et devra être corrigé (cf. chantier 1.2 du plan d'implémentation).

### Utilitaires d'erreur

- `serializeApiErrors()` — mappe les erreurs API vers les champs de formulaire React Hook Form. **Aligné** avec la RFC pour les champs simples, mais à **étendre** pour gérer les chemins imbriqués (422 complexes).
- `getHumanReadableApiError()` — convertit les différents formats d'erreur en message lisible. **À déprécier** au profit de messages contextualisés par feature (cf. RFC, section "Contextualisation des messages d'erreur").
- `assertOrFrontendError()` — assertion TypeScript avec reporting Sentry automatique. **Aligné avec la RFC.**

---

## Problèmes identifiés

### 1. Absence de convention documentée

Il n'existe aucun document décrivant **quand utiliser quel pattern**. Chaque développeur fait son choix au cas par cas, ce qui produit des incohérences :

| Fichier | Pattern utilisé |
|---|---|
| `OfferEducational.tsx` | `serializeApiErrors(error.body, form.setError)` |
| `useSaveVenueSettings.ts` | Boucle manuelle sur `error.body` + `form.setError()` |
| `useSaveOfferLocation.ts` | Boucle manuelle sur `error.body` + `setError()` |
| `ReSendEmailCallout.tsx` | `.catch(() => snackBar.error(...))` sans inspection |
| `StocksCalendar/onSubmit.ts` | `getHumanReadableApiError(error, message)` |

Ces 5 fichiers font essentiellement la même chose (gérer une erreur de mutation) de 5 façons différentes.

### 2. Gestion SWR incohérente et handler global non aligné avec la RFC

Le handler global SWR dans `App.tsx` gère les 404 en redirigeant vers `/404` et affiche un snackbar générique pour le reste. Deux problèmes distincts :

**Handler global non aligné** : la redirection vers `/404` contredit la décision de la RFC qui réserve cette page aux routes inexistantes. Avec la convention "tout est 404" du backend, une route existante peut recevoir un 404 pour une erreur serveur maquillée ; rediriger dans ce cas masque l'erreur à l'utilisateur et casse son contexte de travail.

**Hooks SWR incohérents entre eux** :

- Certains hooks surchargent `onError` localement (ex: `IndividualOfferContext.tsx`)
- Certains hooks n'exploitent pas du tout la propriété `error` retournée (ex: `useVenueAddresses`, `useOffererAddresses`)
- Certains hooks désactivent le retry (`shouldRetryOnError: false`) sans justification claire

Il n'y a pas de convention sur quand surcharger `onError` vs se reposer sur le handler global. La RFC fournit maintenant cette convention (cf. section "Pendant le premier chargement des données d'une page" et chantier 1.2 du plan d'implémentation).

### 3. Problème de typage `T | undefined`

Le client `@hey-api/openapi-ts` est configuré avec `throwOnError: true` et `responseStyle: 'data'`. En pratique, un appel réussi retourne toujours `T`. Mais TypeScript type le retour comme `T | undefined`, forçant des vérifications `undefined` inutiles partout :

```typescript
// Le SDK type le retour comme GetOfferResponseModel | undefined
const offer = await apiNew.getOffer({ path: { offerId } })

// On est forcé de vérifier undefined alors que ça ne peut pas arriver
// (si l'appel échoue, une exception est levée)
assertOrFrontendError(offer, '`offer` is undefined.')
```

Ce problème est un **bloqueur ergonomique** pour la migration vers le nouveau SDK.

### 4. Formats de réponse d'erreur hétérogènes côté backend

Le backend retourne les erreurs sous au moins 4 formats différents :

```json
// Format 1 : champ → message (string)
{ "email": "Adresse email invalide" }

// Format 2 : champ → messages (string[])
{ "email": ["Champ requis", "Format invalide"] }

// Format 3 : code d'erreur
{ "code": "WRONG_UAI_CODE" }

// Format 4 : tableau d'objets
[{ "field1": "message 1" }, { "field2": "message 2" }]
```

Les helpers (`getHumanReadableApiError`, `serializeApiErrors`) tentent de gérer tous ces formats, mais c'est fragile et source de bugs silencieux.

**Contrainte additionnelle identifiée dans la RFC** : pour des raisons de sécurité, le backend masque la majorité des erreurs en 404, ce qui signifie qu'un 404 côté Frontend peut aussi bien correspondre à une ressource inexistante qu'à une vraie erreur serveur (5XX). Seuls les codes 401, 403 et 422 restent interprétables sémantiquement (le maintien des 403 distinctes des 404 étant encore à valider côté Backend).

### 5. Pas de handler global pour les rejections non-catchées

Aucun `window.onunhandledrejection` n'est enregistré. Les promesses rejetées sans `catch` ne sont captées que par l'intégration Sentry par défaut, sans UX utilisateur.

### 6. Pas de pattern de retry/recovery

Aucun mécanisme de retry automatique pour les erreurs transitoires (coupure réseau, 502, 504). Certains hooks SWR désactivent même le retry natif de SWR.

### 7. Pattern legacy de reset de formulaire

`SignIn.tsx` utilise un event listener global sur `document` pour réinitialiser les erreurs de formulaire au clic — un reliquat de Formik qui n'a pas sa place avec React Hook Form.

---

## Nouveaux écarts révélés par la RFC

Les points suivants ne sont pas des "problèmes" au sens strict (le codebase fonctionne aujourd'hui), mais des écarts entre l'état actuel et l'état cible défini dans la RFC. Ils correspondent à des chantiers à planifier.

### 8. Un seul niveau d'Error Boundary existe

Aujourd'hui, seul un `<ErrorBoundary />` au niveau du routeur racine existe (`app/AppRouter/ErrorBoundary.tsx`). La RFC définit une hiérarchie à **trois niveaux** (`<ComponentErrorBoundary />` / `<PageErrorBoundary />` / `<RootErrorBoundary />`) pour contenir les crashes JS au niveau le plus local possible. Tout crash enfant détruit actuellement toute l'application, ce qui est radical et destructif pour l'expérience utilisateur. Chantier 3.1 du plan d'implémentation.

### 9. Page d'erreur statique HTML existante mais mal exploitée

Une URL d'erreur statique **existe déjà** côté infra : `VITE_URL_FOR_MAINTENANCE` pointe vers `https://maintenance.passculture.app?source=<url>`, une page hostée hors bundle React et donc disponible même en cas de crash applicatif. C'est la brique exacte que la RFC demande pour un fallback pré-rendu. Mais son usage actuel présente quatre défauts :

1. **Usage restreint au 503 API**. La redirection n'a lieu que lorsque le backend renvoie un 503. Tous les autres cas d'échec pré-rendu — crash au boot de `index.tsx`, exception pendant l'init de Sentry/Hotjar/orejime, échec de `createRoot()`, erreur de rendu non capturée par une Error Boundary — laissent l'utilisateur sur une page blanche alors que la page statique pourrait servir.
2. **Nom trompeur**. `URL_FOR_MAINTENANCE` et la copy de la page elle-même parlent de "maintenance". Dès qu'on l'utilise pour un crash de bundle, le message ment à l'utilisateur sur la cause du problème. Un renommage (`STATIC_ERROR_PAGE_URL`) et une reformulation côté infra sont nécessaires.
3. **Aucune observabilité**. La redirection est faite silencieusement via `window.location.assign(...)`. Aucun `Sentry.captureException()` ni `flush()` synchrone avant le redirect → aucun signal côté monitoring quand un utilisateur atterrit sur cette page.
4. **Aucun filet au boot**. `index.tsx` n'a aucun try/catch global ; `vite:preloadError` fait `location.reload()` sans compteur (boucle de reload possible). La page statique pourrait pourtant servir de fallback pour ces deux cas.

La cible (cf. RFC, section "Pendant le chargement de l'application") est un usage étendu de cette page statique pour tous les échecs pré-rendu, avec un query param `?reason=...` pour distinguer les cas en support client, et un report Sentry synchrone avant redirect.

### 10. `logout()` fait un hard refresh destructif

La fonction `logout()` (`commons/store/user/dispatchers/logout.ts`) utilise `window.location.href` pour rediriger, ce qui détruit le store Redux. Cela empêche l'affichage d'un toast d'information après la redirection (cas du token d'autologin invalide décrit dans la RFC). Chantier 3.3 du plan d'implémentation.

### 11. `vite:preloadError` sans garde anti-boucle

Le handler `vite:preloadError` dans `index.tsx` recharge la page automatiquement sans limite en cas d'échec de préchargement de chunk. La RFC demande une garde via un compteur `sessionStorage` pour éviter les boucles de reload. Chantier 3.4 du plan d'implémentation.

### 12. Current user et feature flags chargés hors du `route.loader()`

Ces données critiques sont chargées via des hooks (`useUser`, `useLoadFeatureFlags`) qui ne bloquent pas le rendu de la page. La RFC demande un chargement bloquant via `route.loader()` à la racine pour garantir leur disponibilité avant tout rendu de page. Chantier 3.5 du plan d'implémentation.

### 13. Pas de retry policy globale

Aucune configuration SWR globale pour la retry policy. La RFC définit une politique unique : 1 seul retry automatique, avec 1 minute d'attente. Chantier 1.3 du plan d'implémentation.

### 14. Messages d'erreur majoritairement génériques

La plupart des appels API échoués affichent des messages génériques (`GET_DATA_ERROR_MESSAGE`, `SENT_DATA_ERROR_MESSAGE`). La RFC impose une contextualisation systématique (quelle action ou donnée est concernée, quel déclencheur). Critique en contexte B2B. Chantiers 1.8 et 2.3 du plan d'implémentation.

### 15. Convention d'usage des handlers d'erreur non documentée

Les utilitaires `handleError` et `handleUnexpectedError` (à renommer en `handleCaughtError` / `handleInvariantError`, cf. écart #19) ont un rôle simple et invariant : reporter à Sentry **et** notifier l'utilisateur. Ce n'est pas à eux de filtrer ce qui mérite ou non d'être remonté à Sentry — cette décision appartient au call site.

Il manque aujourd'hui une **convention claire** sur quand utiliser ces handlers vs quand appeler directement `snackBar.error(...)`. La règle cible doit être :

- Ces handlers ne sont appelés **que** pour des erreurs que l'on **veut** effectivement logger dans Sentry (erreur inattendue, technique, à investiguer).
- Pour les erreurs métier attendues et à afficher à l'utilisateur sans bruit de monitoring (un 422 avec un message d'erreur de formulaire, par exemple), le call site affiche directement un snackbar via `snackBar.error(...)` sans passer par ces handlers.

Cette convention doit être explicitée dans la RFC et appliquée au fil de la migration Hey API.

### 16. `sendSentryCustomError` redondant avec `handleError` et `handleUnexpectedError`

Le helper `commons/utils/sendSentryCustomError.ts` (20 lignes) fait un sous-ensemble de ce que font déjà `handleError` (Sentry + snackbar) et `handleUnexpectedError` (Sentry + snackbar optionnel via `isSilent`). Il est utilisé à 4 endroits hors-tests :

| Call site | Comportement | Équivalent cible |
|---|---|---|
| `UserReviewDialog.tsx:59` | Sentry + snackbar | `handleCaughtError(e, '...')` |
| `useCollectiveOfferImageUpload.ts:86` | Sentry + snackbar | `handleCaughtError(e, '...')` |
| `formatPrice.ts:62` | Sentry silencieux | `handleCaughtError(e, '...', { isSilent: true })` |
| `orejime.ts:63` | Sentry silencieux | `handleCaughtError(e, '...', { isSilent: true })` |

Son système de tags custom (`'api' | 'data-processing'`) n'est utilisé nulle part hors de sa propre définition : mort-né. Aucune raison de conserver ce helper. À supprimer, les 4 call sites à migrer vers `handleCaughtError` (cf. écart #19), en étendant au passage `isSilent` au premier des deux handlers.

### 17. Helpers ceremoniaux `hasErrorCode`, `getErrorCode`, `getError`

Trois helpers de `apiClient/helpers.ts` ne paient pas leur coût cognitif :

- `hasErrorCode` : type guard utilisé à **1 seul endroit** (`PrebookingButton.tsx:83`, contexte Adage). Le fichier lui-même contient déjà le commentaire `// TODO remove this function because it is use at only one place`.
- `getErrorCode` : wrapper d'une ligne (`error.body.code`) utilisé à **1 seul endroit** (`OfferActionsCell.tsx:173`).
- `getError` : wrapper d'une ligne (`error.body`) dans la même veine.

Ces trois fonctions obscurcissent le code plus qu'elles ne l'aident. Les call sites sont plus lisibles après inline (`isErrorAPIError(error) && error.body?.code === 'NO_BOOKING'`). À supprimer avant la migration pour ne pas les propager.

### 18. Dispersion des helpers d'erreur sur trois dossiers

Le code de gestion d'erreur est réparti entre trois emplacements sans logique apparente :

- `apiClient/helpers.ts` — `serializeApiErrors`, `isErrorAPIError`, `isError`, `getError`, `getErrorCode`, `hasErrorCode`, `getHumanReadableApiError`, + des utilitaires sans rapport (`getFileFromURL`, `HTTP_STATUS`)
- `commons/errors/` — `FrontendError`, `handleError`, `handleUnexpectedError`, `assertOrFrontendError`, `types`
- `commons/utils/sendSentryCustomError.ts` — à supprimer (cf. #16)

`commons/errors/` est déjà le hub naturel pour ces utilitaires. La dispersion actuelle est un reliquat d'évolution non-planifiée et doit être consolidée avant la migration pour que les nouveaux imports générés pointent directement vers le bon endroit. Les non-error utilities (`getFileFromURL`, `HTTP_STATUS`) doivent sortir de `helpers.ts` et rejoindre `commons/utils/`.

### 19. Noms `handleError` / `handleUnexpectedError` sémantiquement trompeurs

Les deux handlers actuels ont des intentions différentes, mais leurs noms ne le reflètent pas :

- `handleError` traite des erreurs **capturées depuis l'extérieur** (API, lib tierce, exception d'un `.toLocaleString()`, `catch (e: unknown)`). Le dev n'est pas responsable de l'existence de l'erreur.
- `handleUnexpectedError` traite des `FrontendError` **instanciés par notre propre code** pour signaler qu'un invariant a été violé (une condition qu'on croyait impossible).

Dans les deux cas, l'erreur est inattendue au sens où aucun dev n'avait prévu la voir arriver. Le nom `handleUnexpectedError` laisse croire que `handleError` traite des cas "attendus", ce qui est faux. Les docstrings confirment d'ailleurs la vraie sémantique :

- `handleError.ts:12` — *"Gracefully handles any **caught** error"*
- `handleUnexpectedError.ts:17` — *"Gracefully handles an unexpected error (= 'that should never happen')"*

Renommage cible : `handleError` → `handleCaughtError`, `handleUnexpectedError` → `handleInvariantError`. Docstrings à réaligner. À faire avant la migration Hey API pour ne pas propager le nom trompeur sur des dizaines de nouveaux call sites.

---

## Cartographie des fichiers clés

### Infrastructure d'erreur

| Fichier | Rôle |
|---|---|
| `apiClient/api.ts` | Point d'entrée API, enregistrement des intercepteurs |
| `apiClient/clientConfig.ts` | Custom fetch (401/503) pour le SDK v1 |
| `apiClient/clientConfigAdage.ts` | Custom fetch pour le SDK Adage |
| `apiClient/compat.ts` | Classe `ApiError` de compatibilité |
| `apiClient/helpers.ts` | Type guards, `serializeApiErrors`, `getHumanReadableApiError`, `HTTP_STATUS` |
| `apiClient/v1/core/request.ts` | Handler HTTP legacy (à supprimer post-migration) |
| `apiClient/v1/core/ApiError.ts` | Classe `ApiError` legacy |
| `apiClient/v1/new/client.gen.ts` | Client généré nouveau SDK avec intercepteurs |

### Gestion des erreurs applicatives

| Fichier | Rôle |
|---|---|
| `commons/errors/FrontendError.ts` | Classe d'erreur pour erreurs internes (non-API) |
| `commons/errors/handleError.ts` | Snackbar + Sentry pour erreurs attendues |
| `commons/errors/handleUnexpectedError.ts` | Snackbar + Sentry enrichi pour erreurs inattendues |
| `commons/errors/assertOrFrontendError.ts` | Assertion TypeScript avec Sentry |
| `commons/errors/types.ts` | Type `FrontendErrorOptions` (contexte Sentry, `isSilent`, etc.) |
| `commons/utils/sendSentryCustomError.ts` | Reporting Sentry avec tags et breadcrumbs |

### UX d'erreur

| Fichier | Rôle |
|---|---|
| `commons/hooks/useSnackBar.ts` | Hook `snackBar.success()` / `snackBar.error()` |
| `commons/core/shared/constants.ts` | Constantes de messages (`GET_DATA_ERROR_MESSAGE`, etc.) |
| `app/App/App.tsx` | Handler SWR global (`onError`) |
| `app/AppRouter/ErrorBoundary.tsx` | Error boundary React Router (Sentry + page "Indisponible") |
| `pages/Errors/NotFound/NotFound.tsx` | Page 404 |
