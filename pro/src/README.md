# DOCS

## Structure du code

Structure du dossier `pro/src/` (Schéma généré avec [cet utilitaire](<https://tree.nathanfriend.com/?s=(%27optiMs!(%27fancy!true~fullPathJ~trailingSlashJ~rootDotJ)~N(%27N%277pro37src36apiClientsUIWMfigWMtextWoreWustom_typesLhooksLstoreLutilsOfactories46c9sLT48TH4EC9GFT.KHOKsOIBAB*6pRsBLPR1B*OIOKs4O51Q851HQE5GAQO52Q852HQF52.KH4AQ6icMsUpublicUrepositoryUstylesUui-kit3%27)~versiM!%271%27)*%20%200**73V*4B**5SousPR6V07%F0%9F%93%81%208%F0%9F%93%98%209ompMentA*%E2%80%A6B3*E%F0%9F%93%95%20F%F0%9F%93%97%20G1.module.scss4H.tsxIcommMsJ!falseKspecL30MonNsource!OB0Q4*RageTC91UB6V%5CnWLc%01WVUTRQONMLKJIHGFEBA98765430*>)) :

```
📁 pro
│
└── 📁 src
    │
    ├── 📁 apiClient    ===> CONFIG ET SERVICES POUR LES APIS (CLIENT PRO, ADRESSE, ADAGE)
    │
    ├── 📁 commons      ===> ÉLÉMENTS PARTAGÉS DANS TOUTE L’APP (HOOKS, STORE REDUX, TYPES, …)
    │   ├── 📁 config
    │   ├── 📁 context
    │   ├── 📁 core
    │   ├── 📁 custom_types
    │   ├── 📁 hooks
    │   ├── 📁 store
    │   └── 📁 utils            ===> UTILITAIRES PARTAGÉS DANS TOUTE L’APP.
    │       └── 📁 factories    ===> FACTORIES POUR LES TESTS UNITAIRES.
    │
    ├── 📁 components    ===> COMPOSANTS FONCTIONNEL TRANSVERSES (SIDENAVLINKS, HEADER, FOOTER, …).
    │   │
    │   ├── 📁 Component1
    │   │   ├── 📘 Component1.tsx
    │   │   ├── 📕 Component1.module.scss    ===> FICHIER DE STYLE (OPTIONNEL)
    │   │   ├── 📗 Component1.spec.tsx       ===> FICHIER DE SPECS (OPTIONNEL) (UNIQUEMENT SI 1 SEUL FICHIER DE TEST)
    │   │   ├── 📁 specs                     ===> DOSSIER DE SPECS (OPTIONNEL) (UNIQUEMENT SI PLUSIEURS FICHIERS DE TEST)
    │   │   └── 📁 commons                   ===> ÉLÉMENTS PARTAGÉS PAR CE COMPOSANT ET SES ENFANTS (OPTIONNEL)
    │   │
    │   └── …
    │
    ├── 📁 pages    ===> PAGES ET COMPOSANTS LIÉS À UNE FEATURE.
    │   │
    │   └── 📁 Page1
    │       │
    │       ├── 📁 commons    ===> ÉLÉMENTS PARTAGÉS PAR CETTE PAGE ET TOUS SES COMPOSANTS ENFANTS (OPTIONNEL)
    │       ├── 📁 specs      ===> DOSSIER DE SPECS POUR CETTE PAGE (OPTIONNEL)
    │       │
    │       ├── 📁 SousPage1
    │       │   ├── 📁 specs      ===> DOSSIER DE SPECS POUR CETTE SOUS-PAGE (OPTIONNEL)
    │       │   ├── 📘 SousPage1.tsx
    │       │   ├── 📕 SousPage1.module.scss
    │       │   └── …
    │       │
    │       └── 📁 SousPage2
    │           ├── 📘 SousPage2.tsx
    │           ├── 📗 SousPage2.spec.tsx
    │           └── …
    │
    ├── 📁 icons
    │
    ├── 📁 public
    │
    ├── 📁 repository
    │
    ├── 📁 styles
    │
    └── 📁 ui-kit    ===> COMPOSANTS D'INTERFACE VALIDÉS PAR LE DESIGN (BUTTONS, INPUTS, …) ET QUI POURRAIENT ÊTRE MIGRÉS DANS DESIGN-SYSTEM à terme
        │
        ├── 📁 Button
        │   ├── 📁 assets    ===> SVGS, ICONS ET IMAGES UTILISÉES DANS LE COMPOSANT UI
        │   ├── 📘 Button.tsx
        │   ├── 📕 Button.module.scss
        │   └── 📕 Button.stories.tsx
        └── …
        │
        └── …
```

> [!TIP]
>
> On peut générer un composant (page, ui-kit, transverse) avec la commande suivante :
>
> ```bash
> pnpm generate:component <nom composant>
> ```
>
> [C.f. documentation détaillée](../scripts/generator/README.md)

---

## [COMPONENTS](./components/README.md)

## [PAGES](./pages/README.md)

## [UI-KIT](./ui-kit/README.md)

## Architecture générale :

La structure des composants visuels suit une organisation par couches :

```
+---------------------------------------------------------------+
|    COMPONENTS : features transverses liées au portail pro     |
+---------------------------------------------------------------+
|    PAGES : pages et composants liées à une seule feature      |
+---------------------------------------------------------------+
|    UI-KIT : composants standards hautement réutilisables      |
+---------------------------------------------------------------+
```

### Chacunes de ces couches obéissent à des règles simples :

- Un élément d’une couche donnée peut importer un élément de même niveau ou de niveau inferieur.
- Un élément d’une couche donnée ne peut jamais importer un élément de niveau supérieur.
- Chaque couche possède un rôle et des règles propres (voir les Readme associés)

## Philosophie / Mantras :

### KISS over DRY, AHA

- préférer la simplicité quitte à répéter un peu de code
- éviter les abstractions hatives

### Ne pas sur-optimiser

Garder un code simple et lisible avant tout. Optimiser le code avant de rencontrer des problèmes de performances peut nous faire risquer la lisibilité et la compréhension du code.

### Garder des fichiers de petite taille

Un fichier est une unité de travail, un développeur devrait pouvoir lire un fichier dans sa totalité et comprendre le fonctionnement général. Si il est dificile de mémoriser l’ensemble des règles et fonctionnement d’un fichier, c'est le signe qu'il faut découper.

## Styles :

### Partager les styles à travers les composants

- Eviter de réutiliser des classes à travers diférents composants
- localiser les styles avec les composants
- créer des composants de mise en page (typographie, boutons, grilles etc...) au lieu de classes globales
- préférer l’usage de variables, mixins ou fonctions pour partager des styles à travers les différents éléments.

À travers l’usage de feuilles de styles globales, il est difficile de déterminer le code utilisé ou mort et de quantifier l’impact d’un changement sur le produit.

### Eviter la surcharge

Ne pas surcharger un élément depuis la feuille de style d’un parent. Cela crée au sein du code base de nombreux couplages qui peuvent avoir des effets de bord sur le long terme. Préférer des composants et l’usage de props pour créer les variantes nécéssaires. (principe Ouvert/fermé)
