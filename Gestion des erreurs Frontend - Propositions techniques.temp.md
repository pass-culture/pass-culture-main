# Gestion des erreurs Frontend — Propositions techniques

> [!NOTE]
> Ce document a été construit et rédigé avec l'assistance de l'IA.

## Objectif

Ce document est un **document de travail temporaire** qui fait le lien entre `Gestion des erreurs Frontend - État des lieux` (liste des écarts à combler) et `Gestion des erreurs Frontend - Tickets JIRA` (tickets actionnables). Pour chaque écart identifié dans l'état des lieux, il propose une ou plusieurs solutions techniques concrètes, avec suffisamment de détails pour à la fois :

- Évaluer la charge de travail et découper les tickets JIRA.
- Guider les développeurs qui implémenteront ces tickets.

> [!IMPORTANT]
> Ce document est **jetable**. Avant sa mise à la poubelle, tout son contenu pertinent doit avoir été intégré dans les descriptions des tickets JIRA correspondants, afin qu'aucune information technique ne soit perdue.

Les décisions de fond (quelle UX, quels patterns cibles) sont définies dans `Gestion des erreurs Frontend - RFC`, qui reste la source de vérité du chantier.

## Classification des chantiers

Les chantiers sont classés en **deux phases** selon leur rapport à la migration `@hey-api/openapi-ts` :

- **Bloquant** — Chantiers à résoudre et coder **avant** que la migration ne commence. Leur absence compromet la migration (anti-patterns introduits partout, types incorrects, conventions non communiquées aux devs migrants). Ces chantiers sont à traiter pendant la Journée Frontend du 2026-04-08 en petits groupes, pour que la migration puisse démarrer le lendemain.
- **Non-bloquant** — Chantiers indépendants des appels API ou qui peuvent être traités **après ou en parallèle** de la migration sans blocage. Incluent les chantiers d'infrastructure (Error Boundaries, hardening du boot) et les patterns avancés (action en lot, workflow multi-mutations).

En plus de ces deux phases, une **checklist transverse** (cf. section 3) liste les critères d'acceptation qui devront être intégrés à chaque ticket de migration d'appel API. Ces items correspondent à du travail par appel et non à des chantiers autonomes : les corriger en dehors de la migration serait de la refacto stérile.

Chaque chantier est décrit avec :

- **Description** : Ce qu'il faut faire concrètement
- **Justification** : Lien avec la RFC ou l'État des lieux
- **Fichiers concernés** : Point de départ technique
- **Niveau de complexité** : Low / Medium / High

---

## 1. Chantiers bloquants

### 1.1 Helper `apiCall<T>` — résolution du problème `T | undefined`

**Description**

Créer un wrapper générique qui transforme le type de retour des appels SDK `Promise<T | undefined>` en `Promise<T>`, en s'appuyant sur la garantie que `throwOnError: true` lève une exception en cas d'échec.

```typescript
// pro/src/commons/errors/apiCall.ts
export async function apiCall<T>(promise: Promise<T | undefined>): Promise<T> {
  const result = await promise
  if (result === undefined) {
    throw new FrontendError(
      'API call returned undefined despite throwOnError: true. This should never happen.'
    )
  }
  return result
}
```

**Justification**

Sans ce helper, chaque appel migré vers le nouveau SDK doit être suivi d'un `assertOrFrontendError(result, ...)` pour gérer le `undefined` typé, ce qui pollue chaque site d'appel. Voir l'écart #3 de l'État des lieux et la section "Codes HTTP côté Frontend" de la RFC.

**Alternative à investiguer** : vérifier si `@hey-api/openapi-ts` propose une option de configuration pour affiner le type de retour quand `throwOnError` est activé. Si oui, c'est une solution plus propre qui évite le wrapper. Cette investigation doit être menée dans le cadre du chantier, pas reportée.

**Fichiers concernés**

- `pro/src/commons/errors/apiCall.ts` (création)
- `pro/src/commons/errors/FrontendError.ts` (existant, utilisé)

**Niveau de complexité** : Low

---

### 1.2 Mise à jour du handler global SWR dans `App.tsx`

**Description**

Aligner le `SWRConfig` global sur la convention "tout est 404" définie dans la RFC :

- **Ne plus rediriger vers `/404`** sur un 404 (une route existante avec données manquantes doit afficher son contenu d'erreur in-place, pas rediriger).
- **Dispatcher un snackbar contextualisé** par défaut pour les erreurs API non gérées localement — si possible, déléguer la contextualisation au composant consommateur via `error` plutôt que d'afficher un message générique.
- Configurer la retry policy (voir 1.3).

**Justification**

La RFC précise que la page `/404` est réservée aux routes inexistantes (non résolvables par le router), pas aux erreurs de chargement. Voir les sections "Pendant le premier chargement des données d'une page" et "Pendant une mise-à-jour des données". Voir aussi l'écart #2 de l'État des lieux.

**Fichiers concernés**

- `pro/src/app/App/App.tsx`

**Niveau de complexité** : Low

---

### 1.3 Retry policy SWR globale

**Description**

Configurer SWR pour retenter automatiquement une erreur **une seule fois**, après une attente d'**une minute**. Au-delà, l'utilisateur doit déclencher manuellement une nouvelle tentative.

```typescript
<SWRConfig
  value={{
    shouldRetryOnError: true,
    errorRetryCount: 1,
    errorRetryInterval: 60000,
    revalidateOnFocus: false,
    onError: (error) => { /* cf. 1.2 */ },
  }}
>
```

**Justification**

Voir la section "Politique de retry sur erreur transitoire" des Règles transversales de la RFC. Voir aussi l'écart #13 de l'État des lieux.

**Fichiers concernés**

- `pro/src/app/App/App.tsx`

**Niveau de complexité** : Low

---

### 1.4 Documenter la convention d'usage des handlers d'erreur

**Description**

Expliciter, dans la RFC puis dans le guide des patterns (cf. 1.7), la **règle d'usage** des handlers `handleCaughtError` / `handleInvariantError` (nouveaux noms, cf. 1.9) :

- Ces handlers ont un rôle simple et invariant : **Sentry + notification utilisateur**. Ils ne filtrent pas et ne doivent jamais filtrer.
- C'est au **call site** de décider si l'erreur mérite d'être remontée à Sentry. La règle :
  - **Erreur inattendue / technique** (5XX masqué en 404, crash JS, erreur réseau, etc.) → appeler un handler pour que ça apparaisse dans Sentry.
  - **Erreur métier attendue avec UX connue** (422 de validation, 403 de droits, 404 "ressource inexistante" attendue, etc.) → afficher directement un snackbar via `snackBar.error(...)` sans passer par les handlers.
- Cette distinction est une règle d'**hygiène du monitoring**, pas une optimisation.

**Justification**

Voir l'écart #15 de l'État des lieux. La politique de logging Sentry de la RFC (section "Politique de logging Sentry") repose sur cette discipline d'usage : les handlers restent simples et "dumb", la responsabilité du filtrage est côté appelant.

**Fichiers concernés**

- `Gestion des erreurs Frontend - RFC` (section "Politique de logging Sentry" : clarifier que le filtrage se fait au call site)
- Documentation des patterns (cf. 1.7)

**Niveau de complexité** : Low (rédactionnel)

---

### 1.5 Extension de `serializeApiErrors` pour chemins imbriqués

**Description**

Étendre `serializeApiErrors` pour gérer les chemins imbriqués des erreurs 422 (champs imbriqués, listes).

Exemple de body 422 à gérer :

```json
{
  "offer.name": "Champ requis",
  "stocks.0.price": "Doit être positif",
  "stocks.1.quantity": "Doit être un entier"
}
```

**Justification**

Voir la section "Pendant une validation de données d'entrée" (validation côté serveur 422) de la RFC. Aujourd'hui, `serializeApiErrors` ne gère pas nativement les chemins imbriqués, ce qui est une limite à lever pour respecter la RFC.

**Fichiers concernés**

- `pro/src/commons/errors/serializeApiErrors.ts` (après déplacement via 1.9)

**Niveau de complexité** : Medium

---

### 1.6 Helper `useApiMutation` pour les mutations API

**Description**

Créer un hook utilitaire qui encapsule le pattern récurrent de mutation API : try/catch + snackbar succès/erreur + serialization des erreurs formulaire + Sentry.

```typescript
const { trigger, isPending } = useApiMutation({
  mutationFn: (values: OfferFormValues) =>
    apiCall(apiNew.postOffer({ body: values })),
  onSuccess: (offer) => {
    snackBar.success('Offre créée avec succès')
    navigate(`/offre/${offer.id}`)
  },
  form, // optionnel : react-hook-form pour le mapping des erreurs 422
  errorMessage: 'Impossible de créer l\'offre.',
})
```

Comportement interne :

- 422 → `serializeApiErrors(error.body, form.setError)` si `form` est fourni, + toast récapitulatif.
- Autre erreur technique → toast avec `errorMessage` + `handleCaughtError` (reporting Sentry).
- Erreur métier connue (403, etc.) → toast spécifique sans handler.

**Justification**

Sans ce helper, chaque mutation migrée doit réimplémenter le même try/catch avec les mêmes étapes, ce qui multiplie les risques d'incohérence. Avec ce helper, la migration des mutations devient quasi-mécanique.

**Fichiers concernés**

- `pro/src/commons/hooks/useApiMutation.ts` (nouveau)

**Niveau de complexité** : Medium

---

### 1.7 Documentation des patterns par phase (référence pour les devs migrants)

**Description**

Rédiger un document de référence (dans `pro/docs/` ou intégré à la RFC) qui présente, pour chaque type d'appel API, le pattern de code à appliquer. Ce document sert de point d'entrée pour tout développeur qui migre un appel, et c'est le document que la checklist transverse (section 3) référence pour chaque critère.

**Contenu attendu** :

- Arbre de décision (quel pattern pour quel cas).
- Exemples de code complets pour chaque pattern (cf. section 4 de ce document).
- Anti-patterns à éviter (avec les items concrets de la checklist transverse, section 3).
- Règle d'usage des handlers d'erreur (cf. 1.4).
- Convention de contextualisation des messages (cf. 1.8).
- Liens vers la RFC et vers les chantiers bloquants (helpers utilisés).

**Justification**

La migration implique de nombreux développeurs qui doivent tous appliquer les mêmes conventions. Sans documentation claire et accessible, la migration va diverger. Ce document est la **source de vérité** référencée par la checklist transverse.

**Fichiers concernés**

- `pro/docs/api-error-handling.md` (nouveau) ou section de la RFC

**Niveau de complexité** : Low (rédactionnel, mais assemble le contenu produit par les autres chantiers bloquants)

---

### 1.8 Convention de contextualisation des messages d'erreur

**Description**

Établir et documenter la convention selon laquelle **tout message d'erreur destiné à l'utilisateur doit être contextualisé** (quelle action ou donnée est concernée, et le déclencheur si pertinent). Les messages génériques comme `GET_DATA_ERROR_MESSAGE` ou `SENT_DATA_ERROR_MESSAGE` ne doivent plus être utilisés comme valeur par défaut.

**Actions** :

- Déprécier (mais ne pas supprimer immédiatement) les constantes de messages génériques dans `commons/core/shared/constants.ts`.
- Ajouter une note dans la documentation (cf. 1.7) pour inciter à la contextualisation.
- Préparer une liste de messages d'exemple par feature pour accompagner les devs migrants.

**Justification**

Voir la section "Contextualisation des messages d'erreur" des Règles transversales de la RFC. Critique en contexte B2B. Voir aussi l'écart #14 de l'État des lieux.

**Fichiers concernés**

- `pro/src/commons/core/shared/constants.ts` (dépréciation des messages génériques)
- Documentation (cf. 1.7)

**Niveau de complexité** : Low

---

### 1.9 Consolidation du code de gestion d'erreur

**Description**

Unifier le code de gestion d'erreur dans `pro/src/commons/errors/` en une seule passe cohérente. Cette consolidation couvre quatre opérations coordonnées :

**(a) Renommage des handlers** (écart #19 de l'État des lieux)

- `handleError` → `handleCaughtError` (pour les erreurs capturées depuis l'extérieur : API, lib tierce, exception d'un `.toLocaleString()`, etc.)
- `handleUnexpectedError` → `handleInvariantError` (pour les `FrontendError` instanciés par notre propre code pour signaler qu'un invariant a été violé)
- Aligner les docstrings avec les nouveaux noms.
- Ajouter un support de `isSilent` à `handleCaughtError` (aujourd'hui seul `handleUnexpectedError` le supporte).

**(b) Suppression de `sendSentryCustomError`** (écart #16)

Le helper `commons/utils/sendSentryCustomError.ts` est redondant avec les deux handlers. Les 4 call sites à migrer :

| Call site | Remplaçant |
|---|---|
| `UserReviewDialog.tsx:59` | `handleCaughtError(e, 'Une erreur est survenue...')` |
| `useCollectiveOfferImageUpload.ts:86` | `handleCaughtError(e, '...')` |
| `formatPrice.ts:62` | `handleCaughtError(e, '...', { isSilent: true })` |
| `orejime.ts:63` | `handleCaughtError(e, '...', { isSilent: true })` |

Le fichier `commons/utils/sendSentryCustomError.ts` est ensuite supprimé.

**(c) Suppression des helpers ceremoniaux** (écart #17)

- `hasErrorCode` (1 call site : `PrebookingButton.tsx:83`) — le fichier source contient déjà un `// TODO remove this function because it is use at only one place`.
- `getErrorCode` (1 call site : `OfferActionsCell.tsx:173`) — wrapper d'une ligne.
- `getError` — wrapper d'une ligne sans call site significatif.

Inliner aux call sites. Exemple :

```typescript
// Avant
if (isErrorAPIError(error) && getErrorCode(error) === 'NO_BOOKING') { ... }
// Après
if (isErrorAPIError(error) && error.body?.code === 'NO_BOOKING') { ... }
```

**(d) Regroupement dans `commons/errors/`** (écart #18)

Déplacer les helpers d'erreur dispersés dans :

- `apiClient/helpers.ts` — `serializeApiErrors`, `isErrorAPIError`, `isError`, `getHumanReadableApiError` (à déprécier, cf. 1.8)
- `commons/utils/sendSentryCustomError.ts` — supprimé (cf. b)

vers `pro/src/commons/errors/` avec un fichier par utilitaire (convention "small files" du projet) :

- `commons/errors/serializeApiErrors.ts`
- `commons/errors/isErrorAPIError.ts` (avec `isError`)
- `commons/errors/getHumanReadableApiError.ts` (à déprécier)

Les non-error utilities qui squattent `apiClient/helpers.ts` sortent également :

- `getFileFromURL` → `commons/utils/file/getFileFromURL.ts`
- `HTTP_STATUS` → `commons/utils/http/httpStatus.ts`

Le fichier `apiClient/helpers.ts` est ensuite supprimé.

**Ordre d'exécution recommandé** (séquentiel, au sein du même ticket) : (a) renommage → (b) suppression sendSentry + inline → (c) suppression helpers ceremoniaux + inline → (d) déplacement des fichiers restants.

**Justification**

Voir les écarts #16, #17, #18 et #19 de l'État des lieux. Cette consolidation doit se faire **avant** la migration : les nouveaux appels migrés pointeront directement vers les bons imports, ce qui évite une deuxième passe de refacto.

**Fichiers concernés**

- `pro/src/commons/errors/handleError.ts` → `handleCaughtError.ts`
- `pro/src/commons/errors/handleUnexpectedError.ts` → `handleInvariantError.ts`
- `pro/src/commons/utils/sendSentryCustomError.ts` (suppression)
- `pro/src/apiClient/helpers.ts` (suppression après déplacement)
- `pro/src/commons/errors/*.ts` (nouveaux fichiers)
- Call sites : `UserReviewDialog.tsx`, `useCollectiveOfferImageUpload.ts`, `formatPrice.ts`, `orejime.ts`, `PrebookingButton.tsx`, `OfferActionsCell.tsx`, + tous les fichiers qui importent les helpers déplacés

**Point de vigilance** : vérifier qu'aucun import circulaire n'apparaît entre `apiClient/` et `commons/errors/` après le déplacement. `commons/errors/` va dépendre de `apiClient/v1` pour importer `ApiError` (sens autorisé). L'inverse ne doit pas être introduit.

**Niveau de complexité** : Medium

---

## 2. Chantiers non-bloquants

### 2.1 Création des Error Boundaries hiérarchiques (3 niveaux)

**Description**

Créer et mettre en place la hiérarchie d'Error Boundaries définie dans la RFC :

- `<ComponentErrorBoundary />` : wrappe les composants (cartes, sections, listes) qui peuvent échouer indépendamment.
- `<PageErrorBoundary />` : wrappe le contenu principal d'une page (`<main>`).
- `<RootErrorBoundary />` : filet de sécurité ultime (existe déjà sous le nom `ErrorBoundary`, à renommer).

**Justification**

Voir la section "Hiérarchie des Error Boundaries" des Règles transversales de la RFC et l'écart #8 de l'État des lieux. Aujourd'hui, seul le niveau 3 existe, ce qui signifie que tout crash JS non rattrapé détruit le contexte de travail de l'utilisateur.

**Fichiers concernés**

- `pro/src/components/ComponentErrorBoundary/` (nouveau)
- `pro/src/components/PageErrorBoundary/` (nouveau)
- `pro/src/app/AppRouter/ErrorBoundary.tsx` → `RootErrorBoundary.tsx` (renommer)
- Tous les layouts de page et composants à wrapper

**Niveau de complexité** : High

---

### 2.2 Hardening de la page d'erreur statique HTML

**Description**

La page d'erreur statique HTML existe déjà côté infra (`URL_FOR_MAINTENANCE` → `https://maintenance.passculture.app`) mais son usage est restreint au 503 API. Étendre son usage et durcir son observabilité.

**Volet Frontend** :

1. **Renommer** `URL_FOR_MAINTENANCE` → `STATIC_ERROR_PAGE_URL` dans `commons/utils/config.ts` et dans tous les call sites.
2. **Créer un helper dédié** `commons/errors/redirectToStaticErrorPage.ts` qui encapsule : `Sentry.captureException(error, { tags: { cause } })` → `Sentry.flush(timeout)` synchrone → `window.location.assign(STATIC_ERROR_PAGE_URL)`. La valeur de `cause` est un paramètre (`'maintenance' | 'bundle-error' | 'preload-error'`), jamais véhiculée par l'URL.
3. **Ajouter un try/catch global dans `index.tsx`** qui appelle le helper avec `cause: 'bundle-error'` en cas d'exception au boot (init Sentry, Hotjar, orejime, `createRoot()`, etc.).
4. **Remplacer les appels directs** `window.location.assign(URL_FOR_MAINTENANCE)` dans les 3 clients HTTP (`clientConfig.ts`, `clientConfigAdage.ts`, `v1/core/request.ts`) par un appel au helper avec `cause: 'maintenance'`.

> [!NOTE]
> La déduplication de la logique 503 entre les 3 clients HTTP est **by design** pendant la migration et n'est pas un objectif de ce chantier. L'usage d'un helper commun permet simplement d'aligner l'observabilité sans modifier l'architecture des clients.

**Volet infra** (à coordonner hors périmètre Frontend) :

- Reformuler le copy de la page statique pour qu'il ne parle plus uniquement de "maintenance" mais couvre l'ensemble des cas d'erreur pré-rendu. Un message générique unique suffit (cf. section "Page d'erreur statique HTML" de la RFC).

Les deux volets peuvent avancer indépendamment.

**Justification**

Voir l'écart #9 de l'État des lieux et la section "Page d'erreur statique HTML" des Règles transversales de la RFC.

**Fichiers concernés**

- `pro/src/commons/utils/config.ts` (renommage)
- `pro/src/commons/errors/redirectToStaticErrorPage.ts` (nouveau)
- `pro/src/index.tsx` (try/catch global)
- `pro/src/apiClient/clientConfig.ts`, `clientConfigAdage.ts`, `v1/core/request.ts` (migration vers le helper)

**Niveau de complexité** : Medium

---

### 2.3 Refacto de `logout()` pour mode "navigation douce"

**Description**

Ajouter un second mode à `logout()` qui utilise React Router au lieu de `window.location.href`. Ce mode permet de conserver le store Redux et donc d'afficher un toast d'information après la redirection.

**Justification**

Voir la section "Pendant le chargement de l'application" de la RFC (cas du token d'autologin invalide) et l'écart #10 de l'État des lieux. Le hard refresh actuel détruit le `snackBarSlice`, empêchant l'affichage d'un toast informatif.

**Fichiers concernés**

- `pro/src/commons/store/user/dispatchers/logout.ts`

**Niveau de complexité** : Medium

---

### 2.4 Compteur `sessionStorage` sur `vite:preloadError`

**Description**

Ajouter une garde anti-boucle au handler `vite:preloadError` existant : au lieu de recharger indéfiniment en cas d'échec de préchargement, limiter à une seule tentative via un compteur en `sessionStorage`. Au-delà, appeler le helper `redirectToStaticErrorPage` (cf. 2.2) avec `cause: 'preload-error'`.

**Justification**

Voir la section "Pendant le chargement de l'application" de la RFC (préchargement de chunk Vite échoué) et l'écart #11 de l'État des lieux. Aujourd'hui, le reload est automatique sans limite.

**Fichiers concernés**

- `pro/src/index.tsx`

**Niveau de complexité** : Low

**Dépendance** : s'appuie sur le helper créé en 2.2.

---

### 2.5 Current user et feature flags via `route.loader()` bloquant

**Description**

Refactorer le chargement du current user et des feature flags pour qu'ils se fassent dans un `route.loader()` à la racine, bloquant le rendu de la page tant qu'ils ne sont pas chargés.

**Justification**

Voir la section "Pendant le chargement de l'application" de la RFC et l'écart #12 de l'État des lieux. Aujourd'hui, ces données sont chargées via des hooks (`useUser`, `useLoadFeatureFlags`) qui ne bloquent pas le rendu, ce qui ne respecte pas la décision prise dans la RFC.

**Fichiers concernés**

- `pro/src/app/AppRouter/AppRouter.tsx`
- `pro/src/app/App/hook/useLoadFeatureFlags.ts`
- `pro/src/commons/store/user/` (dispatcheurs)

**Niveau de complexité** : High

---

### 2.6 Pattern d'action en lot (batch)

**Description**

Définir et implémenter le pattern pour les actions en lot sur plusieurs ressources, avec agrégation des résultats (réussites / échecs) et toast récapitulatif. Idéalement, s'appuyer sur un endpoint batch backend.

**Justification**

Voir la section "Pendant une modification des données" de la RFC. Ce pattern n'est pas urgent pour la migration mais devra être couvert à terme.

**Fichiers concernés**

- `pro/src/commons/hooks/useApiBatch.ts` (nouveau, optionnel)
- Pages utilisant des actions en lot

**Niveau de complexité** : High (nécessite coordination avec le backend)

---

### 2.7 Pattern de workflow multi-mutations (fail-fast)

**Description**

Définir et documenter le pattern pour les workflows qui enchaînent plusieurs mutations en cascade (ex: création d'offre → stock → image → metadata). Approche fail-fast sans rollback, avec toast précisant l'étape d'échec.

**Avertissement** : ce pattern peut laisser des données partiellement créées. Il doit être évité par design quand c'est possible, et accompagné d'un mécanisme de cleanup côté backend sinon.

**Justification**

Voir la section "Pendant une modification des données" de la RFC.

**Fichiers concernés**

- Documentation + cas par cas

**Niveau de complexité** : High (design dépendant)

---

### 2.8 Suppression du legacy `v1/core/request.ts`

**Description**

Une fois la migration suffisamment avancée (tous les appels critiques migrés), supprimer la logique custom de `v1/core/request.ts` qui duplique la gestion 401/503 déjà assurée par `clientConfig.ts`.

**Justification**

Aujourd'hui, la gestion du 401 et du 503 est dupliquée entre l'ancien SDK et le nouveau. Cette duplication disparaît naturellement à la fin de la migration.

**Fichiers concernés**

- `pro/src/apiClient/v1/core/request.ts`

**Niveau de complexité** : Low (suppression)

---

## 3. Checklist transverse — à intégrer dans chaque ticket de migration

Les items ci-dessous ne sont **pas des chantiers autonomes**. Ce sont des critères d'acceptation à intégrer dans la description de **chaque ticket de migration d'appel API** créé après la Journée Frontend. Chaque PR de migration doit satisfaire ces items pour l'appel concerné.

Cette checklist remplace le Tier 2 de l'ancienne classification (tracking tickets qui n'étaient pas de vrais tickets). Elle vit à long terme et doit être copiée verbatim dans chaque ticket de migration.

### 3.1 Checklist à copier dans chaque ticket

```markdown
**Checklist transverse — à cocher pour chaque call migré dans ce ticket**

- [ ] **Helper `apiCall<T>(...)` utilisé** pour l'appel migré (cf. chantier 1.1).
- [ ] **Pattern correspondant au type d'appel appliqué** tel que documenté dans le guide des patterns (cf. chantier 1.7) : Query SWR / Mutation formulaire / Mutation action / Query impérative / Téléchargement / Opération silencieuse / Action UI pure.
- [ ] **Message d'erreur contextualisé** selon la convention (cf. chantier 1.8) : précise l'action ou la donnée concernée, et le déclencheur si pertinent. Aucun usage de `GET_DATA_ERROR_MESSAGE` ou `SENT_DATA_ERROR_MESSAGE` pour cet appel.
- [ ] **Aucune gestion locale du 401 ou du 503** dans le code migré : ces codes sont gérés globalement par `clientConfig.ts`.
- [ ] **Aucune boucle manuelle sur `error.body`** : utiliser `serializeApiErrors` pour mapper les erreurs 422 aux champs de formulaire (cf. chantier 1.5 pour les chemins imbriqués).
- [ ] **Règle d'usage des handlers respectée** (cf. chantier 1.4) : `handleCaughtError` / `handleInvariantError` ne sont appelés que pour les erreurs à logger dans Sentry. Les erreurs métier attendues (422, 403 connus, etc.) utilisent directement `snackBar.error(...)` sans passer par un handler.
- [ ] **Aucun `eslint-disable @typescript-eslint/no-floating-promises` introduit** : toute promesse issue de l'appel migré est awaited ou catchée explicitement.
- [ ] **Upload de fichier géré explicitement** si l'appel concerne un upload (try/catch avec message contextualisé).
- [ ] **Plus de `getHumanReadableApiError`** pour cet appel : remplacé par un message contextualisé (helper déprécié, cf. chantier 1.8).
- [ ] **Aucun event listener global de reset de formulaire** introduit ou laissé en place (pattern Formik legacy).
- [ ] **Tests du call migré à jour** couvrant au minimum : cas nominal, cas d'erreur métier attendue (si pertinent), cas d'erreur technique (reproduit le pattern du guide, cf. chantier 1.7).
```

### 3.2 Source de vérité

Le document de référence pour ces items est **`pro/docs/api-error-handling.md`** (produit par le chantier 1.7). Si un item de la checklist ci-dessus entre en conflit avec ce document, c'est le document qui fait foi.

---

## 4. Patterns de code à appliquer (par phase de la RFC)

### 4.1 Pattern : Query SWR

**Quand l'utiliser** : pour un GET qui charge des données à afficher dans le corps d'un composant. Concerne les phases "Pendant le premier chargement des données d'une page" et "Pendant une mise-à-jour des données".

```typescript
import { apiNew } from '@/apiClient/api'
import { apiCall } from '@/commons/errors/apiCall'
import useSWR from 'swr'

const GET_VENUES_QUERY_KEY = 'GET_VENUES'

export const VenueList = ({ offererId }: Props) => {
  const { data: venues, error, isLoading } = useSWR(
    [GET_VENUES_QUERY_KEY, offererId],
    ([, id]) => apiCall(apiNew.getVenues({ path: { offererId: id } }))
  )

  if (isLoading) return <Spinner />
  if (error) return <ErrorState message="Impossible de charger la liste des lieux." />
  return <VenueTable venues={venues} />
}
```

**Règles** :

- **Ne jamais** try/catch dans le fetcher SWR (SWR ne saurait pas qu'il y a eu une erreur).
- Utiliser `apiCall()` pour garantir un type `T` non-undefined.
- Toujours vérifier `error` et afficher un état d'erreur contextualisé.
- Le handler global (`App.tsx`) dispatche le snackbar et applique la retry policy.

### 4.2 Pattern : Mutation formulaire

**Quand l'utiliser** : pour une soumission de formulaire React Hook Form (POST/PUT/PATCH). Concerne les phases "Pendant une modification des données" et "Pendant une validation de données d'entrée".

**Avec `useApiMutation`** (recommandé) :

```typescript
import { useApiMutation } from '@/commons/hooks/useApiMutation'
import { apiNew } from '@/apiClient/api'
import { apiCall } from '@/commons/errors/apiCall'

const useCreateOffer = (form: UseFormReturn<OfferFormValues>) => {
  const snackBar = useSnackBar()
  const navigate = useNavigate()

  return useApiMutation({
    mutationFn: (values: OfferFormValues) =>
      apiCall(apiNew.postOffer({ body: values })),
    onSuccess: (offer) => {
      snackBar.success('Offre créée avec succès')
      navigate(`/offre/${offer.id}`)
    },
    form,
    errorMessage: 'Impossible de créer l\'offre.',
  })
}
```

**Sans `useApiMutation`** (pour référence, ou cas non couverts) :

```typescript
import { apiCall } from '@/commons/errors/apiCall'
import { isErrorAPIError } from '@/commons/errors/isErrorAPIError'
import { serializeApiErrors } from '@/commons/errors/serializeApiErrors'

const createOffer = async (values: OfferFormValues) => {
  try {
    const offer = await apiCall(apiNew.postOffer({ body: values }))
    snackBar.success('Offre créée avec succès')
    navigate(`/offre/${offer.id}`)
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 422) {
      serializeApiErrors(error.body, form.setError)
      snackBar.error('Le formulaire contient des erreurs.')
    } else {
      snackBar.error('Impossible de créer l\'offre.')
    }
  }
}
```

**Règles** :

- Erreur 422 → mapper les erreurs vers les champs du formulaire via `serializeApiErrors`.
- Autre erreur → snackbar contextualisé (pas de message générique).
- Pour un formulaire multi-étapes, revenir à l'étape qui contient l'erreur.

### 4.3 Pattern : Mutation action

**Quand l'utiliser** : pour une action déclenchée par un bouton (suppression, validation, publication). Concerne la phase "Pendant une modification des données".

```typescript
import { apiCall } from '@/commons/errors/apiCall'
import { isErrorAPIError } from '@/commons/errors/isErrorAPIError'

const handleDelete = async () => {
  try {
    await apiCall(apiNew.deleteOffer({ path: { offerId } }))
    snackBar.success('Offre supprimée')
    await mutate([GET_OFFERS_QUERY_KEY])
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 403) {
      snackBar.error('Vous n\'avez pas les droits pour supprimer cette offre.')
    } else {
      snackBar.error('Impossible de supprimer cette offre.')
    }
  }
}
```

**Règles** :

- Distinguer le 403 (message spécifique aux droits) des autres erreurs.
- Message contextualisé pour l'action concernée.
- Pas de mapping de champs (pas de formulaire).

### 4.4 Pattern : Query impérative

**Quand l'utiliser** : pour un GET déclenché par une action utilisateur hors du cycle de rendu (recherche, chargement à la demande). Concerne la phase "Pendant une mise-à-jour des données".

```typescript
const handleSearch = async (query: string) => {
  try {
    const results = await apiCall(apiNew.searchOffers({ query: { q: query } }))
    setResults(results)
  } catch {
    snackBar.error('La recherche d\'offres a échoué. Veuillez réessayer.')
  }
}
```

**Règles** :

- Même structure que la mutation action.
- Message contextualisé avec l'opération déclenchée par l'utilisateur.

### 4.5 Pattern : Téléchargement / export (opération visible)

**Quand l'utiliser** : pour un téléchargement de fichier, un export CSV, une génération de rapport. Concerne la phase "Pendant une récupération de ressource externe".

```typescript
const downloadInvoice = async (invoiceId: number) => {
  try {
    const blob = await apiCall(apiNew.getInvoicePdf({ path: { invoiceId } }))
    saveAs(blob, `justificatif_${invoiceId}.pdf`)
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 403) {
      snackBar.error('Vous n\'avez pas les droits pour accéder à ce justificatif.')
    } else {
      snackBar.error('Le téléchargement du justificatif a échoué.')
    }
  }
}
```

**Règles** :

- Toujours afficher un toast d'erreur en cas d'échec (l'utilisateur attend un retour).
- Distinguer 403 / autres.
- Les erreurs techniques à logger passent par `handleCaughtError` (cf. 1.4).

### 4.6 Pattern : Opération silencieuse

**Quand l'utiliser** : pour les appels d'analytics, de tracking, de logging d'événement. Concerne la phase "Pendant une récupération de ressource externe" (opération silencieuse).

```typescript
const logTrackingEvent = async (event: TrackingEvent) => {
  try {
    await apiCall(apiNew.logEvent({ body: event }))
  } catch {
    // Silencieux intentionnellement : pas de toast, pas de log Sentry.
    // L'échec d'un appel de tracking ne doit pas perturber l'utilisateur.
  }
}
```

**Règles** :

- Aucun toast, aucun log Sentry.
- Le catch est intentionnellement vide (à documenter avec un commentaire).
- Ne pas utiliser ce pattern pour des appels dont l'échec doit être visible.

### 4.7 Pattern : Action UI pure

**Quand l'utiliser** : pour une action qui utilise une API navigateur native (clipboard, share, fullscreen). Concerne la phase "Pendant une action UI".

```typescript
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    snackBar.success('Copié dans le presse-papier')
  } catch {
    snackBar.error('Impossible de copier dans le presse-papier.')
  }
}
```

**Règles** :

- Pas d'appel réseau → pas d'utilisation de `apiCall`.
- Toast de succès / erreur selon le résultat.
- Pas de log Sentry (erreur souvent liée au contexte utilisateur).

---

## 5. Utilitaires

### 5.1 Cible après consolidation (chantier 1.9)

| Utilitaire | Fichier cible | Usage |
|---|---|---|
| `apiCall<T>(promise)` | `commons/errors/apiCall.ts` | Wrapper résolvant `T | undefined` → `T` (nouveau, cf. 1.1) |
| `isErrorAPIError(error)` | `commons/errors/isErrorAPIError.ts` | Type guard pour identifier une `ApiError` |
| `isError(error)` | `commons/errors/isErrorAPIError.ts` | Type guard générique `Error` (co-located) |
| `serializeApiErrors(body, setError)` | `commons/errors/serializeApiErrors.ts` | Mappe les erreurs API vers les champs React Hook Form (étendu en 1.5) |
| `handleCaughtError(error, msg, opts)` | `commons/errors/handleCaughtError.ts` | Sentry + snackbar pour les erreurs capturées depuis l'extérieur (renommé en 1.9) |
| `handleInvariantError(error, opts)` | `commons/errors/handleInvariantError.ts` | Sentry + snackbar pour les violations d'invariant internes (renommé en 1.9) |
| `assertOrFrontendError(cond, msg)` | `commons/errors/assertOrFrontendError.ts` | Assertion TypeScript + Sentry |
| `FrontendError` | `commons/errors/FrontendError.ts` | Classe d'erreur interne |
| `useApiMutation(options)` | `commons/hooks/useApiMutation.ts` | Hook pour mutations API (nouveau, cf. 1.6) |
| `redirectToStaticErrorPage(error, cause)` | `commons/errors/redirectToStaticErrorPage.ts` | Helper de redirection avec flush Sentry (nouveau, cf. 2.2) |

### 5.2 Supprimés par la consolidation (chantier 1.9)

| Utilitaire | Fichier actuel | Remplaçant |
|---|---|---|
| `sendSentryCustomError` | `commons/utils/sendSentryCustomError.ts` | `handleCaughtError` (avec `isSilent` si besoin) |
| `hasErrorCode` | `apiClient/helpers.ts` | Inline : `error?.body?.code === '...'` |
| `getErrorCode` | `apiClient/helpers.ts` | Inline : `error.body?.code` |
| `getError` | `apiClient/helpers.ts` | Inline : `error.body` |
| `getHumanReadableApiError` | `apiClient/helpers.ts` | Déprécié (cf. 1.8), messages contextualisés par feature |

### 5.3 Déplacés hors de `apiClient/helpers.ts`

| Utilitaire | Fichier actuel | Fichier cible |
|---|---|---|
| `getFileFromURL` | `apiClient/helpers.ts` | `commons/utils/file/getFileFromURL.ts` |
| `HTTP_STATUS` | `apiClient/helpers.ts` | `commons/utils/http/httpStatus.ts` |

Le fichier `apiClient/helpers.ts` est supprimé à la fin du chantier 1.9.

### 5.4 Constantes de messages (dépréciation, cf. 1.8)

Les constantes suivantes sont **dépréciées** au profit de messages contextualisés par feature :

| Constante | Fichier | Statut |
|---|---|---|
| `GET_DATA_ERROR_MESSAGE` | `commons/core/shared/constants.ts` | Déprécié |
| `SENT_DATA_ERROR_MESSAGE` | `commons/core/shared/constants.ts` | Déprécié |
| `FORM_ERROR_MESSAGE` | `commons/core/shared/constants.ts` | Conservé (toast récapitulatif formulaire) |
| `RECAPTCHA_ERROR_MESSAGE` | `commons/core/shared/constants.ts` | Conservé (cas technique spécifique) |

---

## 6. Plan de test pour les patterns de référence

Chaque pattern migré doit inclure des tests couvrant :

### 6.1 Test d'une Query SWR

```typescript
it('should display a contextual error state when the API fails', async () => {
  vi.spyOn(apiNew, 'getVenues').mockRejectedValueOnce(
    makeApiError({ status: 500 })
  )

  renderWithProviders(<VenueList offererId={1} />)

  expect(
    await screen.findByText(/impossible de charger la liste des lieux/i)
  ).toBeInTheDocument()
})
```

### 6.2 Test d'une Mutation formulaire

```typescript
it('should map field errors on 422', async () => {
  vi.spyOn(apiNew, 'postOffer').mockRejectedValueOnce(
    makeApiError({
      status: 422,
      body: { name: ['Ce champ est requis'] },
    })
  )

  renderWithProviders(<CreateOfferForm />)
  await userEvent.click(screen.getByRole('button', { name: /créer/i }))

  expect(await screen.findByText('Ce champ est requis')).toBeInTheDocument()
})

it('should display a contextual error on 500', async () => {
  vi.spyOn(apiNew, 'postOffer').mockRejectedValueOnce(
    makeApiError({ status: 500 })
  )

  renderWithProviders(<CreateOfferForm />)
  await userEvent.click(screen.getByRole('button', { name: /créer/i }))

  expect(
    await screen.findByText(/impossible de créer l'offre/i)
  ).toBeInTheDocument()
})
```

### 6.3 Test d'une Mutation action

```typescript
it('should display a specific message on 403', async () => {
  vi.spyOn(apiNew, 'deleteOffer').mockRejectedValueOnce(
    makeApiError({ status: 403 })
  )

  renderWithProviders(<DeleteOfferButton offerId={1} />)
  await userEvent.click(screen.getByRole('button', { name: /supprimer/i }))

  expect(
    await screen.findByText(/vous n'avez pas les droits/i)
  ).toBeInTheDocument()
})
```

---

## 7. Récapitulatif visuel

```
┌──────────────────────────────────────────────────────────────┐
│                    COUCHE INTERCEPTEURS                       │
│  clientConfig.ts : 401 → logout, 503 → static error page      │
│  (transparent pour tout le code applicatif)                   │
├──────────────────────────────────────────────────────────────┤
│                    COUCHE SWR GLOBALE                         │
│  App.tsx onError : snackbar contextualisé, retry policy       │
│  (gère les queries SWR automatiquement)                       │
├──────────────────────────────────────────────────────────────┤
│                    COUCHE COMPOSANT                           │
│  apiCall() + try/catch dans les handlers de mutations         │
│  et queries impératives (patterns de la section 4)            │
├──────────────────────────────────────────────────────────────┤
│                    COUCHE ERROR BOUNDARIES                    │
│  <ComponentErrorBoundary /> → état d'erreur local             │
│  <PageErrorBoundary /> → titre + callout d'erreur             │
│  <RootErrorBoundary /> → page d'erreur globale (fallback)     │
├──────────────────────────────────────────────────────────────┤
│                    COUCHE FALLBACK ULTIME                     │
│  redirectToStaticErrorPage() + Sentry.flush() synchrone       │
│  Page d'erreur statique HTML hors bundle React                │
├──────────────────────────────────────────────────────────────┤
│                    COUCHE MONITORING                          │
│  Sentry : erreurs techniques uniquement (filtrage au call     │
│  site, cf. chantier 1.4). Handlers : handleCaughtError /      │
│  handleInvariantError.                                         │
└──────────────────────────────────────────────────────────────┘
```
