# DOCS

## [HOOKS](./components/hooks/README.md)
## [UI_KIT](./ui-kit/README.md)
## [COMPONENTS](./new_components/README.md)
## [SCREENS](./screens/README.md)
## [ROUTES](./routes/README.md)
## [REPOSITORY](./repository/README.md)
## [HOCS](./components/hocs/README.md) (DEPRECATED : utiliser les hooks)
## [LAYOUT](./components/layout/README.md) (DEPRECATED : à migrer au sein de components et ui-kit)
## [PAGES](./components/pages/README.md) (DEPRECATED : à migrer dans screens et routes)
## [ROUTER](./components/router/README.md) (DEPRECATED? : à migrer déterminer si migration complète dans routes)


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




