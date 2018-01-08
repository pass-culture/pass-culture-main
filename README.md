# pass-culture-browser

C'est la version (browser) de l'application frontend du Pass Culture.

Staging url - https://staging-pass-culture.netlify.com

Prod url - https://pass-culture.netlify.com

## Install

  Yarn est prometteur, on vous conseille de l'utiliser. Tâchez de l'installer globalement sur votre ordinateur (https://yarnpkg.com/en/docs/install), puis:
  ```bash
    yarn
  ```

## Start
  Pour faire tourner un webpack dev server à http://localhost:3000 et continuer à développer l'application:
  ```bash
    yarn start
  ```

## Deploiement
  Pour déployer le build sur netlify,

  en staging:
  ```bash
    yarn deploy-staging
  ```
  ou en production:
  ```bash
    yarn deploy-production
  ```
