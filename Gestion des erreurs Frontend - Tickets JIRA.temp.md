# Gestion des erreurs Frontend — Tickets JIRA

> [!NOTE]
> Ce document a été construit et rédigé avec l'assistance de l'IA.

## Objectif

Ce document liste les tickets à créer dans JIRA pour combler les écarts identifiés dans `Gestion des erreurs Frontend - État des lieux`, sous l'angle de la stratégie définie dans `Gestion des erreurs Frontend - RFC`.

Chaque ticket doit contenir, dans sa description, **toute l'information technique utile issue de `Gestion des erreurs Frontend - Propositions techniques`** — ce dernier document étant destiné à être jeté une fois la liste de tickets figée. Rien ne doit être perdu.

## Types de ticket

JIRA n'accepte que 3 types de ticket pour ce chantier :

- **Tâche technique** — implémentation directe, pas de décision à prendre.
- **Cadrage technique** — atelier court de décision technique entre devs, débouchant généralement sur une ou plusieurs `Tâche technique`.
- **Cadrage** — atelier métier et/ou design. **Non traité dans cette Journée Frontend** car hors du périmètre dev pur.

## Classification par tier

- **Tier 1** — à traiter **avant** que la migration `@hey-api/openapi-ts` ne commence. Ces tickets sont les **bloquants** pour le démarrage du chantier.
- **Tier 2** — à appliquer **pendant** la migration, au fil des appels migrés.
- **Tier 3** — **plus tard**, après ou en parallèle de la migration sans blocage.

## Contrainte de planification — Journée Frontend du 2026-04-08

Aujourd'hui est la Journée Frontend mensuelle : tous les devs Frontend sont rassemblés pour **boucler en petits groupes tous les tickets Tier 1**, de manière à pouvoir démarrer la migration `@hey-api/openapi-ts` **dès le lendemain**.

Implication : les tickets Tier 1 doivent être soit des `Tâche technique` réalisables dans la journée, soit des `Cadrage technique` courts débouchant immédiatement sur du code. Tout ticket Tier 1 qui serait en réalité un `Cadrage` métier/design doit être **reclassé hors Tier 1** pour ne pas bloquer le démarrage de demain.

## Convention de nommage

Tous les tickets sont préfixés par `[PRO] Migration Hey API - ` dans JIRA.

---

## Tier 1 — Avant la migration

Ces tickets doivent être terminés avant que le premier appel API ne soit migré vers le nouveau SDK. Ils fournissent l'infrastructure (helpers, conventions, documentation) sur laquelle la migration va s'appuyer.

### T1.1 — Créer le helper `apiCall<T>` pour résoudre le problème de typage `T | undefined`

**Titre JIRA** : `[PRO] Migration Hey API - Créer le helper apiCall<T>`

**Chantier** : 1.1 de "Propositions techniques"

**Description**

Créer un wrapper générique `apiCall<T>` dans `pro/src/apiClient/helpers.ts` qui transforme le type de retour `Promise<T | undefined>` du nouveau SDK en `Promise<T>`, en s'appuyant sur la garantie que `throwOnError: true` lève une exception en cas d'échec.

**Critères d'acceptation**

- [ ] Helper `apiCall<T>` créé dans `pro/src/apiClient/helpers.ts`
- [ ] Levée d'une `FrontendError` si le résultat est `undefined` (cas théoriquement impossible mais à protéger)
- [ ] Tests unitaires couvrant les deux branches (résolution normale et levée d'erreur)
- [ ] Documentation JSDoc expliquant l'usage
- [ ] Investigation documentée d'une alternative éventuelle via la configuration `@hey-api/openapi-ts`

**Fichiers concernés**

- `pro/src/apiClient/helpers.ts`
- `pro/src/apiClient/helpers.spec.ts` (à créer ou enrichir)

**Complexité** : Low

**Bloqué par** : aucun
**Bloque** : T1.6, T1.7, début de la migration

---

### T1.2 — Aligner le handler SWR global sur la convention "tout est 404"

**Titre JIRA** : `[PRO] Migration Hey API - Aligner le handler SWR global sur la convention "tout est 404"`

**Chantier** : 1.2 de "Propositions techniques"

**Description**

Mettre à jour le `SWRConfig` global dans `pro/src/app/App/App.tsx` pour supprimer la redirection vers `/404` lors d'un 404 (la page `/404` est réservée aux routes inexistantes, pas aux erreurs de chargement sur une route existante). Le handler doit dispatcher un snackbar par défaut pour les erreurs non gérées localement.

**Critères d'acceptation**

- [ ] Suppression de la redirection `navigate('/404')` dans le `onError` du `SWRConfig`
- [ ] Dispatch d'un snackbar comme comportement par défaut
- [ ] Le handler prend en compte la configuration de retry (voir T1.3)
- [ ] Tests unitaires du nouveau comportement
- [ ] Aucun test existant cassé par le changement

**Fichiers concernés**

- `pro/src/app/App/App.tsx`
- `pro/src/app/App/App.spec.tsx`

**Complexité** : Low

**Bloqué par** : aucun
**Bloque** : début de la migration

---

### T1.3 — Configurer la retry policy SWR globale (1 retry / 1 minute)

**Titre JIRA** : `[PRO] Migration Hey API - Configurer la retry policy SWR globale`

**Chantier** : 1.3 de "Propositions techniques"

**Description**

Configurer les paramètres `shouldRetryOnError`, `errorRetryCount` et `errorRetryInterval` du `SWRConfig` global pour appliquer la politique définie dans la RFC : 1 seul retry automatique, 1 minute d'attente avant retry.

**Critères d'acceptation**

- [ ] `shouldRetryOnError: true`
- [ ] `errorRetryCount: 1`
- [ ] `errorRetryInterval: 60000`
- [ ] Commentaire explicatif dans le code référençant la RFC (section "Politique de retry sur erreur transitoire")
- [ ] Audit des hooks SWR qui désactivent ou surchargent cette configuration (justification ou suppression)

**Fichiers concernés**

- `pro/src/app/App/App.tsx`
- Hooks SWR avec override local de la retry policy

**Complexité** : Low

**Bloqué par** : aucun (peut être fait conjointement avec T1.2)
**Bloque** : début de la migration

---

### T1.4 — Aligner la politique de logging Sentry sur les décisions de la RFC

**Titre JIRA** : `[PRO] Migration Hey API - Aligner la politique de logging Sentry`

**Chantier** : 1.4 de "Propositions techniques"

**Description**

Mettre à jour `handleError`, `handleUnexpectedError` et `sendSentryCustomError` pour qu'ils ne loggent plus automatiquement dans Sentry les erreurs API portant un code métier (401, 403, 404, 422). Seules les erreurs hors codes métier (5XX masqués, erreurs réseau, crashes JS) doivent remonter à Sentry.

**Critères d'acceptation**

- [ ] `handleError` filtre les codes 401/403/404/422 avant d'appeler Sentry
- [ ] `handleUnexpectedError` idem
- [ ] Les crashes JS non-API continuent d'être loggés normalement
- [ ] Tests unitaires couvrant les deux cas (logging et non-logging)
- [ ] Documentation de la politique dans le JSDoc des fonctions, avec référence à la RFC

**Fichiers concernés**

- `pro/src/commons/errors/handleError.ts`
- `pro/src/commons/errors/handleUnexpectedError.ts`
- `pro/src/commons/utils/sendSentryCustomError.ts`
- Tests associés

**Complexité** : Medium

**Bloqué par** : aucun
**Bloque** : début de la migration

---

### T1.5 — Étendre `serializeApiErrors` pour les chemins imbriqués

**Titre JIRA** : `[PRO] Migration Hey API - Étendre serializeApiErrors pour les chemins imbriqués`

**Chantier** : 1.5 de "Propositions techniques"

**Description**

Étendre la fonction `serializeApiErrors` pour qu'elle gère les chemins imbriqués et les indices de listes dans les réponses 422 du backend (ex: `offer.name`, `stocks.0.price`, `stocks.1.quantity`). Ces chemins doivent être correctement mappés vers les champs correspondants dans React Hook Form.

**Critères d'acceptation**

- [ ] Support des chemins à point (`field.subfield`)
- [ ] Support des chemins avec index numérique (`field.0.subfield`)
- [ ] Compatibilité descendante garantie pour les champs simples
- [ ] Tests unitaires couvrant chaque variation de chemin (simple, point, index, combiné)
- [ ] Documentation JSDoc à jour avec exemples

**Fichiers concernés**

- `pro/src/apiClient/helpers.ts`
- `pro/src/apiClient/helpers.spec.ts`

**Complexité** : Medium

**Bloqué par** : aucun
**Bloque** : T1.6, début de la migration

---

### T1.6 — Créer le helper `useApiMutation` pour standardiser les mutations

**Titre JIRA** : `[PRO] Migration Hey API - Créer le helper useApiMutation`

**Chantier** : 1.6 de "Propositions techniques"

**Description**

Créer un hook custom `useApiMutation` qui encapsule le pattern récurrent de mutation API : try/catch + snackbar succès/erreur + serialization des erreurs 422 vers React Hook Form + logging Sentry conditionnel.

**Critères d'acceptation**

- [ ] Hook accepte `mutationFn`, `onSuccess`, `form` (optionnel), `errorMessage`
- [ ] Gestion automatique du 422 via `serializeApiErrors` si `form` est fourni
- [ ] Fallback sur un snackbar avec `errorMessage` pour les autres erreurs
- [ ] Intégration avec la politique Sentry (T1.4)
- [ ] État de chargement exposé (`isPending`)
- [ ] Tests unitaires couvrant : succès, 422 avec form, 422 sans form, 500, erreur réseau
- [ ] Au moins un exemple d'utilisation dans un composant (dans T1.7)

**Fichiers concernés**

- `pro/src/commons/hooks/useApiMutation.ts` (nouveau)
- `pro/src/commons/hooks/useApiMutation.spec.ts` (nouveau)

**Complexité** : Medium

**Bloqué par** : T1.1 (utilise `apiCall`), T1.4 (politique Sentry), T1.5 (422 imbriqués)
**Bloque** : T1.7, début de la migration

---

### T1.7 — Documenter les patterns de gestion d'erreur API

**Titre JIRA** : `[PRO] Migration Hey API - Documenter les patterns de gestion d'erreur API`

**Chantier** : 1.7 de "Propositions techniques"

**Description**

Rédiger un document de référence destiné aux développeurs qui vont migrer les appels API. Ce document doit présenter, pour chaque type d'appel, le pattern de code à appliquer (cf. section 4 de "Propositions techniques"), avec des exemples concrets et les anti-patterns à éviter.

**Critères d'acceptation**

- [ ] Document créé dans `pro/docs/api-error-handling.md` (ou équivalent)
- [ ] Arbre de décision "quel pattern pour quel cas"
- [ ] Exemples de code pour chacun des 7 patterns : Query SWR, Mutation formulaire, Mutation action, Query impérative, Téléchargement, Opération silencieuse, Action UI pure
- [ ] Liste des anti-patterns courants (try/catch dans fetcher SWR, gestion locale 401/503, etc.)
- [ ] Références vers la RFC et vers les helpers créés en T1.1, T1.5, T1.6
- [ ] Document relu et validé par au moins 2 développeurs d'autres squads

**Fichiers concernés**

- `pro/docs/api-error-handling.md` (nouveau)

**Complexité** : Low (rédactionnel)

**Bloqué par** : T1.1, T1.5, T1.6 (helpers à référencer)
**Bloque** : début de la migration

---

### T1.8 — Établir la convention de contextualisation des messages d'erreur

**Titre JIRA** : `[PRO] Migration Hey API - Convention de contextualisation des messages d'erreur`

**Chantier** : 1.8 de "Propositions techniques"

**Description**

Formaliser la convention selon laquelle tout message d'erreur destiné à l'utilisateur doit être contextualisé (quelle action ou donnée est concernée, quel déclencheur). Déprécier les constantes de messages génériques.

**Critères d'acceptation**

- [ ] `GET_DATA_ERROR_MESSAGE` et `SENT_DATA_ERROR_MESSAGE` marqués comme dépréciés (JSDoc `@deprecated`)
- [ ] Commentaire expliquant pourquoi et quoi utiliser à la place
- [ ] Convention documentée dans T1.7
- [ ] Liste de messages d'exemple contextualisés par feature (fichier de référence pour les devs migrants)

**Fichiers concernés**

- `pro/src/commons/core/shared/constants.ts`
- Documentation (T1.7)

**Complexité** : Low

**Bloqué par** : aucun
**Bloque** : T1.7, début de la migration

---

## Tier 2 — Pendant la migration

Ces tickets sont des **tickets de tracking** qui représentent des chantiers répartis sur toute la durée de la migration. Ils ne sont pas réalisés en une seule fois mais progressivement, au fur et à mesure que les appels API sont migrés. Chaque ticket reste ouvert jusqu'à la fin de la migration.

### T2.1 — Appliquer les patterns API à chaque appel migré (tracking)

**Titre JIRA** : `[PRO] Migration Hey API - Appliquer les patterns API à chaque appel migré (tracking)`

**Chantier** : 2.1 de "Propositions techniques"

**Description**

Ticket parapluie de suivi. Chaque PR de migration d'un appel API doit appliquer le pattern correspondant (cf. T1.7 et section 4 de "Propositions techniques") au type d'appel concerné : Query SWR, Mutation formulaire, Mutation action, Query impérative, Téléchargement, Opération silencieuse, Action UI pure.

**Critères d'acceptation**

- [ ] Chaque PR de migration mentionne explicitement le pattern appliqué
- [ ] Aucun appel migré n'utilise d'anti-pattern (try/catch dans fetcher SWR, gestion 401/503 locale, etc.)
- [ ] Le reviewer vérifie la conformité au document T1.7
- [ ] Le ticket est fermé quand tous les appels critiques ont été migrés

**Bloqué par** : T1.7 (documentation des patterns)

---

### T2.2 — Mettre à jour les hooks SWR existants (tracking)

**Titre JIRA** : `[PRO] Migration Hey API - Mise à jour des hooks SWR existants (tracking)`

**Chantier** : 2.2 de "Propositions techniques"

**Description**

Ticket parapluie. Pour chaque hook SWR rencontré pendant la migration, s'assurer qu'il respecte la structure cible : exposer `error`, fournir une valeur par défaut pour `data`, ne pas gérer les erreurs dans le hook. Hooks non conformes déjà identifiés : `useVenueAddresses`, `useOffererAddresses`, `useOffererNamesQuery`.

**Critères d'acceptation**

- [ ] Liste de tracking des hooks non conformes tenue à jour
- [ ] Chaque hook migré expose `error` et a une valeur par défaut pour `data`
- [ ] Les désactivations de retry (`shouldRetryOnError: false`) sont justifiées ou supprimées
- [ ] Le ticket est fermé quand tous les hooks SWR identifiés ont été alignés

---

### T2.3 — Remplacer les messages génériques par des messages contextualisés (tracking)

**Titre JIRA** : `[PRO] Migration Hey API - Remplacement des messages génériques (tracking)`

**Chantier** : 2.3 de "Propositions techniques"

**Description**

Ticket parapluie. Chaque appel migré doit voir ses messages d'erreur génériques (`GET_DATA_ERROR_MESSAGE`, `SENT_DATA_ERROR_MESSAGE`) remplacés par des messages contextualisés précisant l'action ou la donnée concernée.

**Critères d'acceptation**

- [ ] Aucune nouvelle utilisation des constantes dépréciées dans les PR de migration
- [ ] Compteur décroissant des utilisations de `GET_DATA_ERROR_MESSAGE` et `SENT_DATA_ERROR_MESSAGE` dans le codebase
- [ ] Le ticket est fermé quand les dernières utilisations ont été remplacées

**Bloqué par** : T1.8

---

### T2.4 — Corriger les anti-patterns découverts pendant la migration (tracking)

**Titre JIRA** : `[PRO] Migration Hey API - Correction des anti-patterns découverts (tracking)`

**Chantier** : 2.4 de "Propositions techniques"

**Description**

Ticket parapluie. Chaque PR de migration doit corriger les anti-patterns rencontrés dans le code touché : try/catch inutiles dans les fetchers SWR, gestion locale du 401/503, promesses flottantes (`@typescript-eslint/no-floating-promises`), boucles manuelles sur `error.body` au lieu de `serializeApiErrors`, event listener global de reset dans `SignIn.tsx`, etc.

**Critères d'acceptation**

- [ ] Liste des anti-patterns à corriger documentée (lien vers "État des lieux", problèmes #1, #5, #10)
- [ ] Compteur décroissant des suppressions ESLint `no-floating-promises` dans le codebase
- [ ] Le ticket est fermé quand tous les anti-patterns identifiés ont été corrigés

---

## Tier 3 — Plus tard

Ces tickets peuvent être réalisés avant, pendant ou après la migration sans bloquer cette dernière. Ils correspondent à des améliorations d'infrastructure ou à des patterns avancés qui ne sont pas sur le chemin critique.

### T3.1 — Créer la hiérarchie d'Error Boundaries (3 niveaux)

**Titre JIRA** : `[PRO] Migration Hey API - Hiérarchie d'Error Boundaries (3 niveaux)`

**Chantier** : 3.1 de "Propositions techniques"

**Description**

Créer les composants `<ComponentErrorBoundary />` et `<PageErrorBoundary />` (nouveaux), renommer l'existant `<ErrorBoundary />` en `<RootErrorBoundary />`. Intégrer les trois niveaux dans l'application pour contenir les crashes JS au niveau le plus local possible.

**Critères d'acceptation**

- [ ] `<ComponentErrorBoundary />` créé avec état d'erreur local
- [ ] `<PageErrorBoundary />` créé avec titre + callout d'erreur
- [ ] `<RootErrorBoundary />` renommé depuis l'existant `<ErrorBoundary />`
- [ ] Tests unitaires pour chaque niveau
- [ ] Au moins un exemple d'intégration par niveau
- [ ] Documentation dans le document de référence (T1.7)

**Fichiers concernés**

- `pro/src/components/ComponentErrorBoundary/` (nouveau)
- `pro/src/components/PageErrorBoundary/` (nouveau)
- `pro/src/app/AppRouter/ErrorBoundary.tsx` (renommer)
- Layouts de page (intégration)

**Complexité** : High

---

### T3.2 — Créer une page d'erreur statique HTML

**Titre JIRA** : `[PRO] Migration Hey API - Page d'erreur statique HTML`

**Chantier** : 3.2 de "Propositions techniques"

**Description**

Créer une page d'erreur statique HTML servie directement par Firebase hosting, indépendante du bundle React. Cette page prend le relais si le JS crash avant le montage de React.

**Critères d'acceptation**

- [ ] Page HTML statique dans `pro/public/error.html`
- [ ] Design cohérent avec la page d'erreur React existante
- [ ] Configuration Firebase hosting pour servir cette page en cas de crash
- [ ] Test manuel : simuler un crash JS et vérifier l'affichage

**Fichiers concernés**

- `pro/public/error.html` (nouveau)
- Configuration Firebase hosting

**Complexité** : Medium

---

### T3.3 — Ajouter un mode "navigation douce" à `logout()`

**Titre JIRA** : `[PRO] Migration Hey API - Mode "navigation douce" pour logout()`

**Chantier** : 3.3 de "Propositions techniques"

**Description**

Ajouter un second mode à la fonction `logout()` qui utilise React Router au lieu de `window.location.href`. Ce mode préserve le store Redux et permet d'afficher un toast d'information après la redirection (cas du token d'autologin invalide).

**Critères d'acceptation**

- [ ] `logout()` accepte un paramètre `{ mode: 'hard' | 'soft' }`
- [ ] Le mode `soft` utilise React Router
- [ ] Le mode `hard` conserve le comportement actuel (pour les cas où le reset complet du store est nécessaire)
- [ ] Tests unitaires pour chaque mode
- [ ] Mise à jour des appelants qui devraient utiliser `soft`

**Fichiers concernés**

- `pro/src/commons/store/user/dispatchers/logout.ts`
- Appelants identifiés

**Complexité** : Medium

---

### T3.4 — Ajouter une garde anti-boucle sur `vite:preloadError`

**Titre JIRA** : `[PRO] Migration Hey API - Garde anti-boucle sur vite:preloadError`

**Chantier** : 3.4 de "Propositions techniques"

**Description**

Ajouter un compteur en `sessionStorage` au handler `vite:preloadError` existant pour limiter le reload automatique à une seule tentative. Au-delà, l'erreur remonte au `<RootErrorBoundary />`.

**Critères d'acceptation**

- [ ] Compteur persisté dans `sessionStorage`
- [ ] Après 1 reload échoué, l'erreur remonte au `<RootErrorBoundary />`
- [ ] Le compteur est remis à zéro au prochain succès
- [ ] Tests manuels de simulation d'échec de chunk

**Fichiers concernés**

- `pro/src/index.tsx`

**Complexité** : Low

---

### T3.5 — Charger current user et feature flags via `route.loader()` bloquant

**Titre JIRA** : `[PRO] Migration Hey API - Chargement bloquant de current user et feature flags via route.loader()`

**Chantier** : 3.5 de "Propositions techniques"

**Description**

Refactorer le chargement du current user et des feature flags pour qu'ils se fassent dans un `route.loader()` à la racine, bloquant le rendu de la page. Aujourd'hui, ces données sont chargées via des hooks (`useUser`, `useLoadFeatureFlags`) qui ne bloquent pas le rendu.

**Critères d'acceptation**

- [ ] Current user chargé dans le `route.loader()` du root
- [ ] Feature flags chargés dans le `route.loader()` du root
- [ ] Rendu de page bloqué tant que ces données ne sont pas disponibles
- [ ] Mode dégradé conservé pour les feature flags (valeurs par défaut si l'appel échoue)
- [ ] Tests E2E couvrant les cas d'échec
- [ ] Hooks `useUser` et `useLoadFeatureFlags` simplifiés ou supprimés

**Fichiers concernés**

- `pro/src/app/AppRouter/AppRouter.tsx`
- `pro/src/app/App/hook/useLoadFeatureFlags.ts`
- `pro/src/commons/store/user/` (dispatcheurs)

**Complexité** : High

---

### T3.6 — Définir et implémenter le pattern d'action en lot (batch)

**Titre JIRA** : `[PRO] Migration Hey API - Pattern d'action en lot (batch)`

**Chantier** : 3.6 de "Propositions techniques"

**Description**

Définir le pattern pour les actions en lot sur plusieurs ressources, avec agrégation des résultats (réussites / échecs) et toast récapitulatif. Idéalement, s'appuyer sur un endpoint batch backend.

**Critères d'acceptation**

- [ ] Décision sur l'approche (endpoint batch backend ou agrégation client)
- [ ] Helper `useApiBatch` créé (si approche client)
- [ ] Pattern documenté dans le document de référence (T1.7)
- [ ] Au moins un exemple de mise en œuvre dans l'app
- [ ] Coordination avec l'équipe Backend si endpoint batch

**Complexité** : High

**Bloqué par** : coordination Backend potentielle

---

### T3.7 — Définir et documenter le pattern de workflow multi-mutations (fail-fast)

**Titre JIRA** : `[PRO] Migration Hey API - Pattern de workflow multi-mutations (fail-fast)`

**Chantier** : 3.7 de "Propositions techniques"

**Description**

Documenter le pattern fail-fast pour les workflows enchaînant plusieurs mutations en cascade. Identifier les cas existants dans l'app et les risques de données partiellement créées.

**Critères d'acceptation**

- [ ] Pattern fail-fast documenté dans le document de référence (T1.7)
- [ ] Avertissement explicite sur les risques de données partiellement créées
- [ ] Identification des cas existants dans l'app
- [ ] Recommandation cas par cas (cleanup backend ou refonte du workflow)

**Complexité** : High (design dépendant)

---

### T3.8 — Supprimer la logique legacy de `v1/core/request.ts`

**Titre JIRA** : `[PRO] Migration Hey API - Suppression du legacy v1/core/request.ts`

**Chantier** : 3.8 de "Propositions techniques"

**Description**

Une fois tous les appels critiques migrés, supprimer la logique custom de `v1/core/request.ts` qui duplique la gestion 401/503 déjà assurée par `clientConfig.ts`.

**Critères d'acceptation**

- [ ] Migration complète des appels critiques validée
- [ ] Suppression de la logique custom dans `v1/core/request.ts`
- [ ] Aucune régression sur le comportement 401/503
- [ ] Tests E2E de non-régression

**Fichiers concernés**

- `pro/src/apiClient/v1/core/request.ts`

**Complexité** : Low (suppression)

**Bloqué par** : fin de la migration (tickets Tier 2)

---

## Dépendances entre tickets

### Graphe des dépendances Tier 1

```
T1.1 (apiCall) ─────────┐
                        ├──► T1.6 (useApiMutation) ──► T1.7 (doc patterns)
T1.5 (serializeApiErr) ─┘                                    ▲
                                                             │
T1.2 (handler SWR) ──┐                                       │
T1.3 (retry policy) ─┼──► début de la migration ◄────────────┤
T1.4 (politique Sentry) ─┤                                   │
T1.8 (contextualisation) ┘─────────────────────────────────-─┘
```

### Tickets bloquants pour le début de la migration

Tous les tickets Tier 1 sont bloquants. La migration ne doit pas commencer tant que :

- **T1.1** — helper `apiCall` disponible
- **T1.2** + **T1.3** — handler SWR global aligné et retry policy configurée
- **T1.4** — politique Sentry alignée
- **T1.5** — `serializeApiErrors` étendu aux chemins imbriqués
- **T1.6** — helper `useApiMutation` disponible
- **T1.7** — documentation des patterns accessible aux devs migrants
- **T1.8** — convention de contextualisation documentée et messages génériques dépréciés

---

## Estimation globale

- **Tier 1** — 8 tickets, majoritairement Low/Medium. Réalisable en parallèle par 2-3 développeurs sur un sprint court.
- **Tier 2** — 4 tickets de tracking, ouverts pour toute la durée de la migration.
- **Tier 3** — 8 tickets, majoritairement Medium/High. Étalés sur le trimestre ou plus, en parallèle de la migration.
