# pass-culture-pro
to be reverted
C'est la version (browser) de l'application PRO frontend du pass Culture. Ce repo contient également [un storybook](https://pass-culture.github.io/pass-culture-main/?path=/story/ui-kit-checkboxfield--default) des éléments graphiques

Il faut aller voir le README dans https://github.com/betagouv/pass-culture-main pour être informé des différentes lignes de commande associées à ce repo.

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

    - Lancement de la base de donnée pc-postgres (pour l'api) via docker-compose
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

Nous utilisons une bibliotèque faite sur-mesure pour monitorer la dette technique.

voir la documentation ici : https://github.com/gael-boyenval/debt-collector

4 commandes pré-établies sont à disposition :

```
yarn debt:check:changed
yarn debt:check:all
yarn debt:compare
yarn debt:walk
```

Pour plus de details sur sont utilisations sur le portail-pro, vous pouvez consulter la section [debt-collector](./.debt-collector/README.md).

### 1) yarn debt:check:changed

Produit un rapport pour chaque fichiers modifiés depuis master Il est nécéssaire d'avoir master à jour.

### 2) yarn debt:check:all

Produit un rapport pour l'ensemble des fichiers.

### 3) yarn debt:compare

Produit un rapport comparant master à la branche courante en détaillant les fichiers pour lesquels la dette à augmenté, baissé ou stagné.

### 4) yarn debt:walk

Vérifie chaque tag de release, et produit un rapport html complet avec un historique, et divers options de filtrage.

### options

De nombreuse options de filtrages sont disponible en ligne de commande. référez-vous à la [documentation](https://github.com/gael-boyenval/debt-collector) de l'outil pour cela, ou à l'aide du CLI :

```
yarn debt-collector check --help
yarn debt-collector compare --help
yarn debt-collector walk --help
```
