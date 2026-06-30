# Utilisation d'Algolia pour l'app Jeunes

## Résumé

Actuellement Algolia est utilisé directement par l'app pour différentes fonctionnalités dont le but peut se résumer à obtenir une playlist d'objets triés. Exemples :

- Les résultats d'une recherche
- Les offres sur la page Artiste
- Les artistes sur une page Partenaire
- ...

Dans le backend, hors usages du backoffice et du portail pro, on se connecte à Algolia uniquement pour l'indexation des offres, i.e. synchroniser la base de données Algolia avec celle du backend.

Le backend est utilisé par l'app pour charger les données des utilisateurs, des données de configuration, et les données des pages Offre, Partenaire et Artiste.
L'app a donc 2 sources données, qui ne sont presque jamais totalement synchronisées, ce qui a créé de nombreux bugs d'incohérences des données dans l'app. Par exemple, nous n'avons pas implémenté le concept de "produit" dans Algolia, il y a beaucoup d'informations dupliquées entre les offres qui sont rattachées au même produit. Ainsi, lorsqu'une information change sur un produit (comme `last30DaysBookings` qui change quotidiennement), toutes les offres doivent être réindexées, et toutes ne peuvent pas l'être dans le même temps, parce que l'indexation prend du temps. Résultat : si on fait un trie sur les `last30DaysBookings`, on ne peut pas garantir l'offre qui remontera en 1er, et peut-être que ce sera parmi les offres d'un même produit celle qui est la plus éloignée de l'utilisateur.

De plus, l'interface avec Algolia est bien différente de celle du backend et le typage (des offres notamment) s'en retrouve confus, d'autant plus que dans Algolia, il n'y a pas champ dont la présence est garantie : tous sont optionnels.
L'une des contraintes majeures du développement mobile est la rétrocompatibilité avec les anciennes versions toujours en service.
Donc si on veut supprimer une donnée dans le backend, il faut attendre qu'elle ne soit plus utilisée par aucune version de l'app en service. Autrement dit, il faut attendre qu'il y ait une mise à jour forcée de l'app sur les stores, et donc que la version minimale en service soit montée.
Dans le backend, on contourne ce problème en faisant des nouvelles versions des routes utilisées par l'app, qu'on accumule jusqu'à la prochaine MàJ forcée, après laquelle on peut supprimer les versions de routes qui ne sont plus utilisées.
Malheureusement, on ne peut pas versionner Algolia : il n'y a qu'une seule instance pour toutes les versions de l'app et on ne peut pas se permettre d'avoir plusieurs versions des mêmes données (les limites de stockage de notre contrat avec Algolia ne le permettent pas).
Cette contrainte fait qu'après plusieurs années d'utilisation, on a accumulé beaucoup de données dans nos objets Algolia, au fur et à mesure du développement de nouvelles fonctionnalités, sans être capable de supprimer régulièrement ce qui n'est plus utilisé. Aussi, les usages d'Algolia dans l'app se sont multipliés.

Algolia est un outil spécialisé pour la recherche, et nous offre des performances bien meilleures que celles qu'on pourrait avoir avec le backend pour les mêmes fonctionnalités, particulièrement avec la recherche géographique.

L'idée est d'améliorer cette situation, c'est-à-dire d'atténuer les problèmes actuels :

- fort couplage de l'app avec Algolia
- incohérences ponctuelles des données
- complexité du code

## Propositon

Appeler Algolia seulement avec le backend.
