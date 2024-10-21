# Bonnes pratiques

## Comment attendre

Les mauvaises implémentations de codes d'attentes sont les principales sources d'instabilité (flakiness) dans les tests E2E, soyez vigilants ! Les mauvaises pratiques sont :

- [les tests conditionnels sur un DOM instable](https://docs.cypress.io/guides/core-concepts/conditional-testing)
- attendre qu'un élément disparaisse en utilisant "cet élément ne devrait pas être visible" alors que l'élément n'est pas encore apparu : le test passe mais trop tôt, c'est un faux positif.
- utiliser `cy.wait(1000)` pour un élément qui doit apparaitre : vous ne savez pas vraiment quand l'élément va arriver, donc ça va échouer si l'app est un peut trop lente ou alors vous allez attendre plus longtemps que néccessaire et ralentir l'exécution des tests.

**à la place :**

1. utilisez les `intercept` fournis par Cypress pour attendre les retours du serveur avant d'interagir avec les éléments de l'UI.
2. n'attendez pas des éléments instables comme les animations, essayez de penser à d'autres moyens d'attendre que l'app atteigne un certain état.
3. définissez des constantes de timeouts avec un bon nommage dans `support/timeouts.ts`, en mettant des timeouts courts pour que les tests ne tournent pas trop longtemps dans le cas où l'élément attendu n'apparait pas à cause d'un bug (note: cette règle n'est pas encore en place dans le projet).
