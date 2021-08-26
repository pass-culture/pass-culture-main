# pass-culture-pro

[![Coverage Status](https://coveralls.io/repos/github/betagouv/pass-culture-pro/badge.svg?branch=master)](https://coveralls.io/github/betagouv/pass-culture-pro?branch=master)

C'est la version (browser) de l'application PRO frontend du pass Culture.

Il faut aller voir le README dans https://github.com/betagouv/pass-culture-main
pour être informé des différentes lignes de commande associées à ce repo.

## Note sur Yarn

Yarn est prometteur, on vous conseille de l'utiliser. Tâchez de l'installer globalement sur votre ordinateur (https://yarnpkg.com/en/docs/install), puis:
```bash
  yarn
```

## Installation et Lancement de l'application Pro
- ```shell
  yarn install
  yarn start
  ```

## Lancement des tests

- ### Lancement des tests unitaires
  ```shell
  yarn test:unit
  ```

- ### Lancement des tests end to end

  - Prérequis aux lancement des tests e2e testcafe (⚠️**Depuis le repository api**)
    - Lancement de la base de donnée pc-postgres (pour l'api)  via docker-compose
      ```shell
      docker-compose -f ../docker-compose-app.yml up -d postgres
      ```
    - Injection des données de test
      ```shell
      export DATABASE_URL=postgresql://pass_culture:passq@localhost:5434/pass_culture && python src/pcapi/install_database_extensions.py && alembic upgrade head && rm -rf ./src/pcapi/static/object_store_data
      python src/pcapi/scripts/pc.py sandbox -n testcafe
      ```

  - Lancement des tests depuis la ligne de commande (⚠️**Depuis le repository pro**)
    ```shell
    yarn test:cafe
    ```

## Standards de code et d'architecture

La documentation est intégrée au projet, aux travers de fichiers README à la racine des dossiers principaux.

Vous trouverez une documentation générale ainsi que des liens vers les différents README en suivant ce lien :

[Standards de code et d'architecture](./src/README.md)

## Dette technique

Nous utilisons un outil nommé Tyrion afin de visualiser et de suivre l'évolution de notre dette technique. 
Tyrion se base sur les commentaires de code pour produire des rapports de dette technique. 
Nous invitons les développeurs à ajouter des commentaires à leur guise pour marquer les parties du code qui leur semble complexe, peu compréhensible, déprécié etc...

### la syntaxe pour ajouter un commentaire de dette : 

```
/*
* @debt <label> "<author-name> : mon commentaire"
*/
```

les labels sont les suivants :

- **directory** : quand le fichier en question ne suit pas [les standards de notre architecture](./src/README.md)
- **bugRisk** : quand le code représente un risque de bug 
- **securityRisk** : quand le code représente un risque de securité 
- **complexity** : quand un fichiers ou une partie du code est trop compliqué à comprendre ou trop long
- **standard** : quand le code ne suit pas nos standards de code
- **testWarning** : quand le test (ou fichier de test) génère des warning (proptypes, act, unhandled promise etc...)
- **testInitialize** : quand le fichier de test n'a pas de fonction d'initialisation (banc de test)
- **rtl** : quand le fichier de test doit être migré de enzyme vers react-testing-library
- **deprecated** : quand un bout de code fait usage d'une fonctionalité ou outil à dé-commissioner
- **duplicated** : quand un bout de code est dupliqué, ou que plusieurs éléments devraient être regroupé en un seul


### lancer tyrion : 

`dept:report` : génère un rapport de la dette actuelle
`dept:tendency` : génère un rapport sur l'évolution de la dette durant les 100 derniers commits