# Documentation

## Accès rapide
* [hooks](./components/hooks/README.md)
* [ui-kit](./ui-kit/README.md)
* [components](./new_components/README.md)
* [screens](./screens/README.md)
* [routes](./routes/README.md)
* [repository](./repository/README.md)
* [hocs](./components/hocs/README.md) (DEPRECATED : utiliser les hooks)
* [layout](./components/layout/README.md) (DEPRECATED : à migrer au sein de components et ui-kit)
* [pages](./components/pages/README.md) (DEPRECATED : à migrer dans screens et routes)
* [router](./components/router/README.md) (DEPRECATED? : à migrer déterminer si migration complète dans routes)


## Architecture de l'application:

Voir aussi une structure possible [en suivant atomic design](./doc/structure-atomic-design.md)

```
    // Root.tsx est l'entré de l'application.
    // On y:
    //   * fait les appel api necessaire à la configuration général et
    //   * configure l'application ( features / user )
    //   * fait les appel api necessaire à la configuration général et
    //   * instancie les Providers globaux et App.
├── Root.tsx
|
├── api/  // toutes nos interaction avec fetch, notamment notre client api généré via swagger codegen
|
|   // ui-kit est une bibliotéque de petit composant réutilisable
|   // Button, Select, Title, etc
├── ui-kit/
|
|   // components contient tout les composants réutilisé/
├── components/
|
|   // routes gére les appel api et la mise en forme des données necessaire à chaque screen
├── routes/
|
|   // templates contient tout les tempalte de page ou de morceau de page réutilisable
|   // App, Form, Page, Filters, etc
├── templates/
|
|   // screen fait la glue entre les donné et fourni par la route, les element de template et les composants.
└── screens/
```

## Architecture générale :


La structure des composants visuels suit une organisation par couches :

```
+---------------------------------------------------------------+
|    THEME : nos variables, mixins et fonctions SCSS            |
+---------------------------------------------------------------+
|    UI-KIT : composants standards hautement réutilisables      |
+---------------------------------------------------------------+
|    COMPONENTS : features intermédiaires                       |
+---------------------------------------------------------------+
|    SCREENS : écrans non connéctés et sans la nav générale     |
+---------------------------------------------------------------+
|    ROUTES : routage, hydratation des screens, chargement      |
+---------------------------------------------------------------+
```

### Chacunes de ces couches obéissent à des règles simples :

- Un élément d'une couche donnée peut importer un élément de même niveau ou de niveau inferieur.
- Un élément d'une couche donnée ne peut jamais importer un élément de niveau supérieur.
- Chaque couche possède un rôle et des règles propres (voir les Readme associés)

## Philosophie / Mantras :

### KISS over DRY, AHA

- préférer la simplicité quitte à répéter un peu de code
- éviter les abstractions hatives

### Ne pas sur-optimiser

Garder un code simple et lisible avant tout.
Optimiser le code avant de rencontrer des problèmes de performances peut nous faire risquer la lisibilité et la compréhension du code.

### Garder des fichiers de petite taille

Un fichier est une unité de travail, un développeur devrait pouvoir lire un fichier dans sa totalité et comprendre le fonctionnement général.
Si il est dificile de mémoriser l'ensemble des règles et fonctionnement d'un fichier, c'est le signe qu'il faut découper.


## Styles :

### Partager les styles à travers les composants

- Eviter de réutiliser des classes à travers diférents composants
- localiser les styles avec les composants
- créer des composants de mise en page (typographie, boutons, grilles etc...) au lieu de classes globales
- préférer l'usage de variables, mixins ou fonctions pour partager des styles à travers les différents éléments.

À travers l'usage de feuilles de styles globales, il est difficile de déterminer le code utilisé ou mort
et de quantifier l'impact d'un changement sur le produit.


### Eviter la surcharge

Ne pas surcharger un élément depuis la feuille de style d'un parent. Cela crée au sein du code base de nombreux couplages qui peuvent avoir des effets de bord sur le long terme. Préférer des composants et l'usage de props pour créer les variantes nécéssaires. (principe Ouvert/fermé)




