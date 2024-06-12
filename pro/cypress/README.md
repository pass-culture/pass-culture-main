# Bonnes pratiques

## Les couches d'implémentations

features (Gherkin) -> step-definitions (TS) (et c'est tout !)

-   [Gherkin](#writing-your-first-scenario-with-gherkin) : c'est le fichier `.feature`. C'est ici que vous décrivez le cas d'usage fonctionnel comme si vous étiez un utilisateur sans connaissance technique. Tout le monde dans l'entreprise devrait être capable de comprendre et de reproduire le cas de test. Ici, vous éviterez de parler de la façon dont le test est implémenté, par exemple "l'utlisateur se connecte" plutôt que "l'utilisateur remplit le champ ..."
-   [Step definition](#step-definition) : ici vous collez à l'interface et décrivez chaque interaction. Chaque personne qui lit le code devrait être capable de reproduire le cas de test comme si c'était un script. Pour faciliter la lecture du code, on a utilisé Testing Library (voir plus bas). 

## Les fichiers .feature

Gherkin est un langage non technique et compréhensible par les humains pour écrire un scénario de test. Il est interprété par Cucumber pour faire le lien avec les step definitions dans Typescript. Regardez ce que vous pouvez faire avec Gherkin dans cette [documentation](https://cucumber.io/docs/gherkin/reference/), il faut absolument savoir comment utiliser ces mots clé avant d'écrire votre premier scénario :

-   Feature
-   Background
-   Scenario
-   Scenario Outline and Examples
-   Step Arguments (doc string, data tables, etc.) et les Expressions Cucumber inclus dans cette [documentation dédiée](https://github.com/cucumber/cucumber-expressions#readme)

TODO: parler des tags?

### Comment nommer votre Feature et Scenario

La "feature" doit décrire où vous êtes dans l'application et l'objectif d'un point de vue utilisateur. On reprend souvent juste en dessous le modèle "En tant que ... j'aimerais ... afin de...", sur trois lignes distinctes.
Le scénario devrait entrer plus dans les détails et décrire brièvement ce qu'il vérifie. Le titre du scénario doit être unique.

_Ex:_
Feature: Create and update venue
  Scenario: A pro user can add a venue without SIRET
  Scenario: A pro user can add a venue with SIRET
  Scenario: It should update a venue

Utilisez `Given`, `When`, `Then`, `And`, `But` dans le bon ordre pour rendre vos scénarios faciles à lire :

-   `Given` donne les préconditions : que doit-on faire pour arriver à notre objet de test
-   `When` décrit les actions : dans le contexte de ma fonctionalité, quelles sont les étapes à réaliser pour atteindre mon résultat
-   `Then` attend un résultat et fait une assertion
-   `And`, `But` lie des étapes, ce sont des alias des trois mots clés précédents

**Réutilisez** des étapes: quand vous tapez un mot, votre IDE devrait vous donner des indices sur des steps proches ou existantes (il faut parfois installer un plugin gherkin ou cucumber).
Vous pouvez aussi utiliser les paramètres de steps pour appeler la même step mais avec des données différentes.

Pour les nouvelles steps, veuillez suivre les règles suivantes :

-   commencer en minuscule
-   décrire qui fait quoi: `EXEMPLE` (si possible, utiliser "the user" ou un rôle spécifique suivi d'un verbe d'action)
-   décrire ce qui doit être vérifié: `EXEMPLE`

:information_source: Les bonnes pratiques de gherkin recommandent de n'utiliser pas plus de **un** couple de `When`/`Then` dans un test, même si c'est difficile à mettre en place dans une configuration end-to-end.

Vous pouvez ensuite déclarer la définition de votre nouvelle step dans le fichier TS correspondant.

### Examples

```
Feature: Create and update venue

  Background:
    Given I am logged in

  Scenario: A pro user can add a venue without SIRET
    When I want to add a venue
    And I choose a venue which already has a Siret
    And I add venue without Siret details
    And I validate venue step
    And I skip offer creation
    Then I should see my venue without Siret resume
    
    [...]
```    

## Step definition

Elle commence par un mot clé Gherkin (`Given`, `When`, `Then` => ce n'est pas important), suivi de l'expression cucumber. Elle doit rester courte, parfois contenir quelques interactions avec le navigateur, et/ou contenir des assertions.

### Examples

```
Given('I want to add a venue', () => {
  cy.findByLabelText('Structure').select('Bar des amis')
  cy.findByText('Ajouter un lieu').click()
})

When('I choose a venue which already has a Siret', () => {
  cy.findByText('Ce lieu possède un SIRET').click()
})

[...]

Then('Paramètres généraux data should be updated', () => {
  cy.findByText('Musée de France').should('be.visible')
})
```

## Comment attendre

Les mauvaises implémentations de codes d'attentes sont les principales sources d'instabilité (flakiness) dans les tests E2E, soyez vigilants ! Les mauvaises pratiques sont :

-   [les tests conditionnels sur un DOM instable](https://docs.cypress.io/guides/core-concepts/conditional-testing)
-   attendre qu'un élément disparaisse en utilisant "cet élément ne devrait pas être visible" alors que l'élément n'est pas encore apparu : le test passe mais trop tôt, c'est un faux positif.
-   utiliser `cy.wait(1000)` pour un élément qui doit apparaitre : vous ne savez pas vraiment quand l'élément va arriver, donc ça va échouer si l'app est un peut trop lente ou alors vous allez attendre plus longtemps que néccessaire et ralentir l'exécution des tests.

**à la place :**

1. utilisez les `intercept` fournis par Cypress pour attendre les retours du serveur avant d'interagir avec les éléments de l'UI.
2. n'attendez pas des éléments instables comme les animations, essayez de penser à d'autres moyens d'attendre que l'app atteigne un certain état.
3. définissez des constantes de timeouts avec un bon nommage dans `support/timeouts.ts`, en mettant des timeouts courts pour que les tests ne tournent pas trop longtemps dans le cas où l'élément attendu n'apparait pas à cause d'un bug (note: cette règle n'est pas encore en place dans le projet).