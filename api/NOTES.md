# BO — sortir des composants de Bootstrap

Branche de discussion, jamais mergée.

## Objectif

Appliquer la charte UI (tokens + composants) du design sans la traduire dans le système Bootstrap, trop opinionated (taxonomie `primary`/`secondary`… = couleurs, là où le DS parle de niveaux d'emphase).

## Critère de tri : qui porte le comportement et l'a11y ?

| Catégorie | Composants | Traitement |
| --- | --- | --- |
| Présentationnels | button, input, select, textarea, checkbox/radio/switch, badge/tag, alert, card, table, link | Sortis de Bootstrap : HTML + CSS maison |
| Comportementaux | modal, dropdown, collapse/accordion, tabs, tooltip/popover, toast, offcanvas | Restent Bootstrap (JS, focus, clavier, ARIA, Popper), habillés via les variables CSS `--bs-*` |
| Layout / utilitaires | grid, `d-*`, `m*-*`, `p*-*` | Hors périmètre (~1650 occurrences). Au plus : aligner `$spacer` sur l'échelle d'espacement |

## Inventaire

Comptage statique (2026-09-29) : classes Bootstrap dans les templates BO (hors `dev/`), les chaînes Python de `routes/backoffice/` et le JS `static/backoffice/js/{addons,core}`. `Occ.` = occurrences, `Fich.` = fichiers. Migration incrémentale, un composant par PR ; l'ordre du tableau est l'ordre suggéré (du plus centralisé au plus diffus).

### À migrer

| Composant | Occ. | Fich. | Classes actuelles | Remarque |
| --- | --- | --- | --- | --- |
| Badge | ~290 appels | 62 | `badge text-{cat} bg-{cat}-subtle` | Point d'entrée unique : `format_badge()` (`routes/backoffice/filters.py:856`) + filtres dérivés (`format_bool_badge`…) |
| Champs de formulaire | ~340 champs | 17 templates | `form-control`, `form-select`, `form-check-input`, `form-switch`, `form-floating` | Rendu centralisé dans `templates/components/forms/*.html`. Champs : texte ~156, select simple ~80, textarea ~38, date ~37, switch 28, checkbox 2, fichier 2. Tous en label flottant (`form-floating`) → placement du label à trancher par le design |
| Input group | 21 | 11 | `input-group`, `input-group-text` | Avec les champs |
| États de validation | 8 | 1 | `is-invalid`, `is-valid`, `invalid-feedback` | Posés par le JS uniquement → contrat à préserver |
| Button | 534 | 104 | `btn` 291, `btn-sm` 84, `btn-outline-primary-subtle-bg` 76 (custom, `pc/_buttons.scss`), `btn-primary` 35, `btn-outline-primary` 24, `btn-md` 11, `btn-link` 5 | Le plus diffus. Les `data-bs-toggle` portés par les boutons restent (comportement ≠ style) |
| Button group | 13 | 8 | `btn-group`, `btn-group-sm` | Avec Button |
| Close button | 8 | 8 | `btn-close` | Avec Button |
| Link | 100 | 38 | `link-primary` | 24 occurrences générées en Python |
| Alert | 31 | 10 | `alert`, `alert-{warning,info,danger}`, `alert-dismissible` | |
| Card | 150 | 36 | `card`, `card-body`, `card-title`, `card-subtitle`, `card-text`, `card-header` | `card-columns` = reliquat Bootstrap 4 |
| Table | 107 | 42 | `table`, `table-hover`, `table-light`, `table-borderless`, `table-secondary` | 23 occurrences en JS (table manager, tri, pagination, multi-select) → contrats |
| List group | 34 | 2 | `list-group`, `list-group-item`, `list-group-flush` | |
| Progress | 12 | 8 | `progress`, `progress-bar` | Addon custom `pc/addons/_progress_bar.scss` |
| Pagination | 9 | 2 | `pagination`, `page-item`, `page-link` | 5 occurrences en JS (`pc-table-paginator.js`) |
| Breadcrumb | 7 | 4 | `breadcrumb`, `breadcrumb-item` | |
| Spinner | 3 | 2 | `spinner-border`, `spinner-grow` | |

### À garder sous Bootstrap (habillés via `--bs-*`)

| Composant | Occ. | Fich. | Classes actuelles | Raison |
| --- | --- | --- | --- | --- |
| Modal | 327 | 72 | `modal*`, `data-bs-toggle="modal"` 138 | Focus trap, clavier ; `bootstrap.Modal` appelé par le JS (`pc-form.js`…) |
| Dropdown | 191 | 40 | `dropdown`, `dropdown-menu`, `dropdown-item`, `data-bs-toggle="dropdown"` | Popper, navigation clavier |
| Tooltip | 51 | 27 | `data-bs-toggle="tooltip"` | Popper, init par `bs-tooltips.js` |
| Nav / tabs | 42 | 6 | `nav`, `nav-link`, `nav-item`, `nav-underline`, `nav-pills`, `tab-pane` | Onglets pilotés par le JS ; styles déjà surchargés (`pc/_nav.scss`) |
| Accordion | 22 | 9 | `accordion*` | |
| Collapse | 17 | 9 | `collapse`, `data-bs-toggle="collapse"` | |
| Navbar | 4 | 2 | `navbar`, `navbar-brand`, `navbar-text` | Layout global |
| Offcanvas | 4 | 1 | `offcanvas*` | |
| Tom Select | ~146 champs | — | thème `tom-select-bootstrap-5.min.css` | Lib tierce (select multiple, autocomplete) calée sur les classes Bootstrap |
| Date range picker | 8 champs | — | `vanilla-datetimerange-picker` | Lib tierce dérivée de bootstrap-daterangepicker |

### Hors périmètre (utilitaires)

| Famille | Occ. | Fich. | Classes les plus fréquentes |
| --- | --- | --- | --- |
| Espacements | 918 | 155 | `mb-1`, `p-0`, `px-3`, `mt-4`, `mb-3` |
| Display / flex | 467 | 116 | `d-flex`, `d-block`, `d-none`, `align-items-center` |
| Grille | 264 | 70 | `row`, `col-6`, `col-4`, `col` |
| Couleurs | 118 | 58 | `text-muted`, `text-warning`, `text-secondary`, `text-primary` |

Les utilitaires de couleur restent, mais leurs valeurs viennent des variables BO via les `--bs-*` : c'est là que les tokens passent sans rien migrer.

## Règles

- **Nommage** : le DS est la SSOT. Classes préfixées (`.pc-button--secondary`) pour éviter les collisions avec Bootstrap (`.badge`, `.dropdown`…) et pouvoir grep le périmètre migré.
- **Cohabitation** : sortir un composant = retirer l'import du partial Bootstrap correspondant (`_buttons.scss`, `_forms.scss`…). On retire du CSS, on n'en ajoute pas. Aujourd'hui `pc/pc.scss` importe `bootstrap/bootstrap` en bloc → le remplacer par la liste explicite des partials, sans toucher au vendor.
- **Contrats JS** : avant de sortir les forms, recenser qui lit les classes Bootstrap (`.is-invalid`, `.was-validated`, `.form-control`, addons, datetime picker).
- **Composants petits** : quelques dizaines de lignes, pilotés par les variables, sans logique. Sinon → il aurait dû rester Bootstrap.
- **Macros Jinja** : seulement pour du balisage à invariants (checkbox + label + erreur + `aria-describedby`). Sinon classes lisibles directement dans le template.
- **Documentation** : la page DS dev (`/dev/components`) devient la référence officielle, construite au fil de l'eau.

## Tokens et DS pass Culture

- `@pass-culture/design-system` publie des tokens en variables CSS (`lib/pro`, `lib/jeune`), pas de thème BO.
- Uniformisation actée pour Pro + Jeune seulement, en chantier. Le BO n'est pas dans le périmètre.
- Composants DS = React → non réutilisables. Leurs `*.module.scss` (`pro/src/design-system/`) servent de spec de référence.
- Donc : **variables CSS propres au BO** pour l'instant. Brancher le BO sur les tokens `pro` = décision du design, à leur poser comme question, pas à imposer.
- Levier : une couche BO déjà pilotée par variables rend l'intégration future du BO quasi gratuite pour le design (on change la source des variables).
- Si un jour on consomme le paquet : version épinglée, pour ne pas subir le chantier Pro/Jeune.

## Proposition

1. Composants présentationnels hors Bootstrap, nommés DS, pilotés par variables CSS.
2. Source des variables : fichier BO. Question ouverte au design : le BO rejoint-il l'uniformisation ?
3. Composants comportementaux : Bootstrap, habillés via `--bs-*` alimentés par ces mêmes variables.

Seul le point 2 dépend d'une autre équipe ; il ne bloque ni 1 ni 3.

Migration incrémentale, composant par composant (stratégie validée avec le design, sous réserve d'adoption par l'équipe).
