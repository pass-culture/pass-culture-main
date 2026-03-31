# App

<!-- Run `npx doctoc src/app/README.md` to update it -->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Rendu d'une page](#rendu-dune-page)
- [Responsabilités](#responsabilit%C3%A9s)
- [Permissions](#permissions)
  - [Page par défaut et autorisation d'accès aux espaces](#page-par-d%C3%A9faut-et-autorisation-dacc%C3%A8s-aux-espaces)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Rendu d'une page

```mermaid
flowchart TB
    PATH(["/a-path"])
    PATH --> INDEX_FILE["src/index.tsx"]
    INDEX_FILE --> ROOT_COMPONENT["&lt;Root />"]
    ROOT_COMPONENT --> APP_ROUTER_COMPONENT["&lt;AppRouter /&gt;"]

    APP_ROUTER_COMPONENT --> ROUTER_PROVIDER

    subgraph ROUTER_PROVIDER["&lt;RouterProvider /&gt;"]
        direction TB
        FIND_ROUTE[\"Find the route\n(matching 'route.path')"/]
        FIND_ROUTE --> RUN_LOADER[\"Run 'route.loader()'"/]
        RUN_LOADER --> RUN_GUARD[\"'route.loader' calls 'withUserPermissions()'"/]
        RUN_GUARD --> IS_USER_ALLOWED{"Is the user allowed?"}
        IS_USER_ALLOWED --> |Yes| RENDER_APP
        IS_USER_ALLOWED --> |No| REDIRECT_TO_DEFAULT_PAGE[/"Redirect to default page\n'redirect(getUserDefaultPath())'"\]
        REDIRECT_TO_DEFAULT_PAGE --> FIND_ROUTE
    end

    subgraph RENDER_APP["Render Application"]
        direction TB
        APP_COMPONENT["&lt;App /&gt;"]
        APP_COMPONENT --> PAGE["Page Component\n(via &lt;Outlet /&gt;)"]
    end
```

## Responsabilités

Dans la mesure du possible, chaque responsabilité globale ou transverse doit être gérée par **une et une seule fonction** (util, composant, hook, etc).

| Scope         | Rôle | Fonction |
| ------------- | ---- | -------- |
| User          | (Re-)Charger l'ensemble des entités et structures,<br>ce qui (re-)sélectionne automatiquement la bonne entité et structure pour chaque espace. | `initializeUser()` |
| User          | Quelle est l'ID de l'entité à sélectionner pour l'espace d'administration selon l'état actuel de l'application ? | `getInitialAdminOffererId()` |
| User          | Quelle est l'ID de la structure à sélectionner pour l'espace partenaire selon l'état actuel de l'application ? | `getInitialPartnerVenueId()` |
| User          | Changer d'entité pour l'espace d'administration. | `setSelectedAdminOffererById()` |
| User          | Changer de structure pour l'espace partenaire. | `setSelectedPartnerVenueById()` |
| User          | Quelles sont les permissions de l'utilisateur ? | `getCurrentUserPermissions()` |
| Routing, User | Quel est le chemin de sa page par défault ? | `getUserDefaultPath()` |

## Permissions

Les permissions sont calculées à partir du state Redux par la fonction `getCurrentUserPermissions()`.

| Flag                               | Description métier                                                                                         |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `isAuthenticated`                  | Est-il authentifié ?                                                                                       |
| `hasSelectedParnerVenue`           | A-t-il une structure séléctionnée (espace partenaire) ?                                                    |
| `isSelectedPartnerVenueAssociated` | La structure sélectionnée est-elle rattachée à ce compte (= le rattachement a-t-il été validé) ?           |
| `hasSelectedAdminOfferer`          | A-t-il un entité séléctionnée (espace d'administration) ?                                                  |
| `isSelectedAdminOffererAssociated` | L'entité sélectionnée est-elle rattachée à ce compte (= le rattachement a-t-il été validé) ?               |
| `isOnboarded`                      | Une offre a-t-elle déjà été créée sur une des structures de l'entité parenet à la structure sélectionnée ? |

### Page par défaut et autorisation d'accès aux espaces

Selon :
- les structures et entités auxquelles l'utilisateur a accès (valides et en attente de validation),
- son entité sélectionnée ou non pour son espace d'administration,
- sa structure sélectionnée ou non pour son espace partenaire,

ce schéma répond à ces questions :
- Quelle est sa page par défaut ?
- A-t-il le **droit** d'accéder au Hub ? (en entrant `/hub` dans sa barre d'adresse)
- A-t-il un bouton pour accéder au Hub sur sa page par défaut ?
- A-t-il le **droit** d'accéder à l'espace d'administration ? (en entrant `/administration` dans sa barre d'adresse)
- A-t-il un bouton pour accéder à l'espace d'administration sur sa page par défaut ?

```mermaid
flowchart TD
    HAS_SOME_VENUES{"L'utilisateur a au moins une structure ?"}
    HAS_MULTIPLE_VENUES{"L'utilisateur a plusieurs structures ?"}
    HAS_SELECTED_VENUE{"L'utilisateur a une structure sélectionnée ?"}
    IS_SELECTED_VENUE_ASSOCIATED{"La structure sélectionnée est-elle rattachée ?"}
    IS_SELECTED_VENUE_ONBOARDED{"La structure sélectionnée est-elle onboardée ?"}

    AUTOSELECT_OFFERER[/"`On auto-sélectionne la première entité _(1)_`"\]
    AUTOSELECT_VENUE[/"`On auto-sélectionne la seule structure _(2)_`"\]
    GO_TO_NEW_VENUE[\"L'utilisateur va sur l'ajout d'une nouvelle structure"/]
    style GO_TO_NEW_VENUE stroke-dasharray: 5 5

    HAS_SOME_VENUES --> | Oui | AUTOSELECT_OFFERER
    HAS_SOME_VENUES --> | Non | FIRST_VENUE_PAGE["- Page par défaut : Ajout d'une nouvelle structure\n- Hub : Non\n- Administration : Non"]

    AUTOSELECT_OFFERER --> HAS_MULTIPLE_VENUES
    AUTOSELECT_OFFERER -.- GO_TO_NEW_VENUE

    GO_TO_NEW_VENUE -.-> NEW_VENUE_PAGE["`Hub (UX) : Oui _(3)_<br>Hub (URL) : Oui<br>Administration (UX) : Non<br>Administration (URL) : Oui`"]
    style NEW_VENUE_PAGE stroke-dasharray: 5 5

    HAS_MULTIPLE_VENUES --> | Oui | HAS_SELECTED_VENUE
    HAS_MULTIPLE_VENUES --> | Non | AUTOSELECT_VENUE
    AUTOSELECT_VENUE --> IS_SELECTED_VENUE_ASSOCIATED

    HAS_SELECTED_VENUE --> | Oui | IS_SELECTED_VENUE_ASSOCIATED
    HAS_SELECTED_VENUE --> | Non | HUB_PAGE["- Page par défaut : Hub\n- Hub : Oui\n- Administration : Oui"]

    IS_SELECTED_VENUE_ASSOCIATED --> | Oui | IS_SELECTED_VENUE_ONBOARDED
    IS_SELECTED_VENUE_ASSOCIATED --> | Non | NON_ATTACHED_VENUE_PAGE["- Page par défaut : Non-rattachement\n- Hub : Oui\n- Administration : Oui"]

    IS_SELECTED_VENUE_ONBOARDED --> | Oui | HOME_PAGE["- Page par défaut : Accueil\n- Hub : Oui\n- Administration : Oui"]
    IS_SELECTED_VENUE_ONBOARDED --> | Non | ONBOARDING_PAGE["- Page par défaut : Onboarding\n- Hub : Oui\nAdministration (UX) : Non\nAdministration (URL) : Oui"]
```

> [!NOTE]  
> _(1) Première entité de la liste, ordonnée par nom, tout état confondu (= y compris en attente de rattachement)._  
> _(2) Première structure de la liste, ordonnée par nom, tout état confondu (= y compris en attente de rattachement)._  
> _(3) Seulement sur la première étape de l'ajout de structure, via un bouton "Annuler et quitter"._
