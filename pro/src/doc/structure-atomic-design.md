## Structure du projet

### Proposition de structure cible

Voir le live disponible en ligne [à cette address](https://atomicdesign.bradfrost.com/table-of-contents/)

Architecture cible atomic design

```
├── Root.tsx // entré de l'application
|
├── components/ // composants réutilisé parmis plusieurs screen et features
|   ├── atoms/  // composant visuel sans state ni interactions.
|   |   └── ...
|   ├── moleculs/  // group de 2 à 3 atoms, gère leurs interaction et leurs dépendences de styles
|   |   └── ...
|   └── organisms/  // composant implementant de grosse fonctionalités. Peut contenir des atoms, moleculs ou d'autre organisms.
|       └── ...
|
├── features/ // grandes section fonctionnel: auth, offer, booking, etc
|   ├── booking
|   |   ├── adaptors/ // adateur api réutilisé par plusieurs routes (type api -> type composant)
|   |   |   └── ...
|   |   ├── atoms/  // composant visuel sans state ni interactions.
|   |   |   └── ...
|   |   ├── moleculs/  // group de 2 à 3 atoms, gère leurs interaction et leurs dépendences de styles
|   |   |   └── ...
|   |   ├── organisms/  // composant implementant de grosse fonctionalités. Peut contenir des atoms, moleculs ou d'autre organisms.
|   |   |   └── ...
|   |   ├── types.ts
|   |   └── constants.ts
|   └── etc
|
├── templates/  // tempalte de page ou de morceau de page réutilisable
|   ├── App
|   ├── Page
|   ├── Form
|   ├── SearchFilters
|   └── etc
├── routes/  // contient des routes qui gère les interaction api et leurs transformation (adapteur api -> screen)
|   └── etc
|
|   // utilise un ou plusieurs template, des données et callback api et
|   // des composants venant de ui-kit et/ou feature pour rendre une page ou un morceau de page.
└── pages/
    └── etc
```