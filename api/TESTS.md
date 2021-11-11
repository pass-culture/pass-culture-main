# Tests automatisés

Les tests automatisés sont écrits et exécutés avec pytest.

## Indépendance des tests

Aujourd'hui, la plupart des tests ne sont pas réellement indépendants : ils dépendant des données générées par d'autres tests
exécutés plus tôt. Le souhait est de les rendre exécutable indépendamment des autres.

* Pour ce faire, on peut décorer une fonction de test avec `@clean_database` qui va s'occuper de vider toutes les tables dans la base de donnée.
Un test décoré de cette manière va donc devoir se préoccuper d'enregistrer les données dont il a besoin.

## Niveaux de tests

On reconnaît 3 niveaux de tests : unitaire, integration, fonctionnel.

### Unitaires

Un test unitaire est défini comme un test qui s'applique à une portion du code que l'on a écrit tout en étant totalement
indépendant de tout système externe à l'application : base de donnée, web service, horloge système, etc.

### Integration

Un test d'intégration est défini comme un test qui s'applique à une portion du code que l'on a écrit tout en étant
dépendant d'un ou plusieurs systèmes externes à l'application : base de donnée, web service, horloge système, etc.

### Fonctionnel

Un test fonctionnel est défini comme un test qui s'applique à une portion du code que l'on a écrit tout en étant
dépendant d'un ou plusieurs systèmes externes à l'application : base de donnée, web service, horloge système, etc.
La différence avec un test d'intégration est qu'il teste du point de vue d'un utilisateur. Dans le contexte d'une API web,
l'utilisateur est une single page application et le point d'entrée sont les routes d'API. On testera donc via les routes d'API.