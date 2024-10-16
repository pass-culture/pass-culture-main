**Sommaire**

- [Générer un composant](#générer-un-composant)
- [Générer un fichier d'utilitaire](#générer-un-fichier-dutilitaire)

# Générer un composant

Générer un composant du nom de **MyComponent** :

```bash
yarn generate:component MyComponent
```

Cela va demander le dossier dans lequel le composant devra être créé :

```
? Target directory? (Use arrow keys or type to search)
❯ /Users/jm-culture/Work/pass-culture-main/pro/src
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/__specs__
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage/core
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage/models
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage/services
(Move up and down to reveal more choices)
```

Vous pourrez ensuite choisir si vous souhaitez générer les fichiers pour le module SCSS, les tests et les stories :

```
✔ Generate SCSS module? (Use arrow keys)
❯ Yes
  No

✔ Generate test file? (Use arrow keys)
❯ Yes
  No

✔ Generate storybook file? (Use arrow keys)
❯ Yes
  No
```

À la fin, un résumé sera présenté avant confirmation définitive :

```
This will generate all these files:

/Users/jm-culture/Work/pass-culture-main/pro/src/components
└─ MyComponent
   ├─ MyComponent.tsx
   ├─ MyComponent.module.scss
   ├─ MyComponent.spec.tsx
   └─ MyComponent.stories.tsx

✔ Is that ok? (Y/n)

Successfully generated files:

 - /Users/jm-culture/Work/pass-culture-main/pro/src/components/MyComponent/MyComponent.tsx
 - /Users/jm-culture/Work/pass-culture-main/pro/src/components/MyComponent/MyComponent.module.scss
 - /Users/jm-culture/Work/pass-culture-main/pro/src/components/MyComponent/MyComponent.spec.tsx
 - /Users/jm-culture/Work/pass-culture-main/pro/src/components/MyComponent/MyComponent.stories.tsx
```

# Générer un fichier d'utilitaire

Générer un utilitaire du nom de **mySuperUtil** :

```bash
yarn generate:util mySuperUtil
```

Cela va demander le dossier dans lequel le composant devra être créé :

```
? Target directory? (Use arrow keys or type to search)
❯ /Users/jm-culture/Work/pass-culture-main/pro/src
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/__specs__
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage/core
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage/models
  /Users/jm-culture/Work/pass-culture-main/pro/src/apiClient/adage/services
(Move up and down to reveal more choices)
```

Vous pourrez ensuite choisir si vous souhaitez générer le fichier de specs :

```
✔ Generate test file? (Use arrow keys)
❯ Yes
  No
```

À la fin, un résumé sera présenté avant confirmation définitive :

```
This will generate all these files:

/Users/jm-culture/Work/pass-culture-main/pro/src/utils
└─
   ├─ mySuperUtil.ts
   └─ mySuperUtil.spec.ts

✔ Is that ok? yes

Successfully generated files:

 - /Users/jm-culture/Work/pass-culture-main/pro/src/utils/mySuperUtil.ts
 - /Users/jm-culture/Work/pass-culture-main/pro/src/utils/mySuperUtil.spec.ts
```
