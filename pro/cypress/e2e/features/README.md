# Guidelines Gherkin

## Dois-je écrire ce test ?

### Assurez vous que votre test est un bon candidat pour être un test end-to-end

Peut-être que si vous voulez vérifier un bouton radio ou les messages d'erreur dans un formulaire, ce n'est pas la peine de rajouter un test end-to-end pour ça ? Si vous pouvez ajouter ces vérifications dans des tests de composants, d'API ou même un test unitaire, c'est encore mieux !

### Vérifiez que le test que vous voulez écrire n'existe pas déjà

Comme dit dans le titre, ne réécrivez pas un test (ou une assertion) qui existe déjà ailleurs. Regardez bien qu'il n'y a pas déjà un autre scénario qui vérifie ce que vous voulez couvrir avant d'écrire votre test.

## Ecrivez de beaux scénarios que tout le monde aura envie de lire

### Nommez vos features et scénarios de manière à ce qu'on sache exactement ce qu'ils vont faire

En lisant votre feature et votre scénario on devrait savoir immédiatement ce que ça teste.
Pour trouver l'inspiration, on pourra par exemple utiliser une tournure à la Friends : "Celui où..."

### Faites le plus court possible

Evitez au maximum d'avoir des scénarios longs, complexes à lire. Peut-être que si c'est trop long c'est que vous voulez tester trop de choses à la fois? Ensuite, lisez le point suivant :

### Un scénario, une vérification

Essayez, autant que possible, de vérifier une seule chose par scénario. Cela peut être un défi parce que cela va mettre en péril la performance de vos tests, mais au moins essayez.

Exemple de tests qui respectent bien ces deux règles : les scénarios Adage.

### Seule et unique exception aux deux points précédents

la seule exception tolérée dans le contexte Pass Culture sera le cas des parcours (workflow) nominaux (happy path) et critiques: ce que souhaite faire l'utilisateur et qui ne doit jamais casser. Dans ces cas spécifiques, il vaut mieux un parcours de bout en bout que des petits scénarios découpés de façon artificielle et couteuse en préconditions (mocks par exemple).

### Ne décrivez pas l'interface utilisateur (UI)

votre scénario ne devrait pas parler de l'interface (boutons, liens, etc.). Vous devriez parler de l'intention de l'utlisateur plutôt que de ses interactions.

_Ex:_ `I click on "Plus Tard" link in confirmation popin`_, devrait plutôt ressembler à :_ `I skip offer creation`


## Gardez le projet propre

### La règle du boy scout

On doit laisser le code plus propre qu'on ne l'a trouvé. Cela veut dire que si vous trouvez quelque chose qui devrait être corrigé, corrigez le.

_Ex: variable mal nommée, typo, etc..._