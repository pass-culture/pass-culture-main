# Exécution des tests e2e Cypress avec le Pass Culture

Pour exécuter les tests, vous avez besoin de la stack lancée en local et **aucune donnée dans la sandbox** (les données utiles pour chacun des cas de test sont créés à l'exécution de chacun d'entre eux).

## Stack Pass Culture Pro dans Docker
Le plus simple est de lancer l’application `pro` avec `docker-compose`. Cela permet de lancer en une commande les containers `pc-nginx`, `pc-backoffice`, `pc-api`, `pc-postgres-pytest`, `pc-postgres` et `pc-redis` 

Pour cela, avec une version node récente, dans le répertoire [`pass-culture`](https://github.com/pass-culture/pass-culture-main) :

Dans un premier terminal:
```
pass-culture-main % ./pc symlink
pass-culture-main % pc install
pass-culture-main % docker-compose -f docker-compose-backend.yml up -d
pass-culture-main % pc start-pro
```
Et c’est tout. Il ne faut pas peupler la sandbox, elle doit rester vide et les données seront créées par la Factory lors de l’exécution.

## Lancer les tests avec l'interface Cypress
Pour lancer les tests avec l'interface Cypress et ainsi avoir la possibilité de revenir sur l'exécution sans marquer de points d'arrêts, il faut lancer la commande suivante depuis le répertoire `pro` dans un second terminal:
```
pro % yarn test:e2e
```
puis sélectionner le fichier `.cy.ts` à exécuter dans l'interface ou choisir de tout lancer (voir l'[open mode](https://docs.cypress.io/app/core-concepts/open-mode])).

## Lancer les tests sans l'interface Cypress
Sans l'interface Cypress, et donc en ligne de commande, il faut exécuter la commande suivante depuis le répertoire `pro`:
```
pro % yarn test:bdd
```

Pour ne lancer qu'un seul fichier de test `.cy.ts` on peut le sélectionner avec l'option `--spec` dans cette commande:
```
pro % npx cypress run --e2e --browser chrome --config-file cypress/cypress.config.ts --spec cypress/e2e/adageConfirmation.cy.ts
```

# Données générées - Data Factory
Nous n'utilisons plus les données de la sandbox industrial et générons nos propres données avec des routes Factory.

De nouvelles routes `api` sont créées par les devs. Voir par exemple
```
api/src/pcapi/sandboxes/scripts/getters/pro_01_create_pro_user.py
```
qu’il suffit d’appeler ainsi dans les tests auto dans son test e2e en récupérant les données.

Exemple:
```typescript
cy.request(
    'http://localhost:5001/sanboxes/pro_01_create_pro_user/create_pro_user_with_venue_bank_account_and_userofferer'
  ).then((response) => {
    expect(response.status).to.eq(200)
    user_email = response.body.user.email
  })
  ```

# Bonnes pratiques

## Comment attendre ?

Les mauvaises implémentations de codes d'attentes sont les principales sources d'instabilité (flakiness) dans les tests E2E, soyez vigilants ! Les mauvaises pratiques sont :

- [les tests conditionnels sur un DOM instable](https://docs.cypress.io/guides/core-concepts/conditional-testing)
- attendre qu'un élément disparaisse en utilisant "cet élément ne devrait pas être visible" alors que l'élément n'est pas encore apparu : le test passe mais trop tôt, c'est un faux positif.
- utiliser `cy.wait(1000)` pour un élément qui doit apparaitre : vous ne savez pas vraiment quand l'élément va arriver, donc ça va échouer si l'app est un peut trop lente ou alors vous allez attendre plus longtemps que néccessaire et ralentir l'exécution des tests.

**à la place :**

1. utilisez les `intercept` fournis par Cypress pour attendre les retours du serveur avant d'interagir avec les éléments de l'UI.
2. n'attendez pas des éléments instables comme les animations, essayez de penser à d'autres moyens d'attendre que l'app atteigne un certain état.
3. définissez des constantes de timeouts avec un bon nommage dans `support/timeouts.ts`, en mettant des timeouts courts pour que les tests ne tournent pas trop longtemps dans le cas où l'élément attendu n'apparait pas à cause d'un bug (note: cette règle n'est pas encore en place dans le projet).