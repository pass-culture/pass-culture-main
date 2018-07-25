# Tests automatisés

Les tests automatisés sont écrits avec pytest.
On reconnaît 3 types de tests : unitaire, integration, functionnel.

## Unitaires

Un test unitaire est défini comme un test qui s'applique à une portion du code que l'on a écrit tout en étant totalement
indépendant de tout système externe à l'application : base de donnée, web service, horloge système, etc.

## Integration

Un test d'intégration est défini comme un test qui s'applique à une portion du code que l'on a écrit tout en étant
dépendant d'un ou plusieurs systèmes externes à l'application : base de donnée, web service, horloge système, etc.

## Fonctionnel

Un test fonctionnel est défini comme un test qui s'applique à une portion du code que l'on a écrit tout en étant
dépendant d'un ou plusieurs systèmes externes à l'application : base de donnée, web service, horloge système, etc.
La différence avec un test d'intégration est qu'il teste du point de vue d'un utilisateur. Dans le contexte d'une API web,
l'utilisateur est une single page application et le point d'entrée sont les routes d'API. On testera donc via les routes d'API.