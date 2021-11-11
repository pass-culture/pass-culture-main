# Package `validation.models`

Les modules de ce package contiennent des fonctions de validation d'un modèle
(cf. le CONTRIBUTING à la racine du projet pour savoir les différents niveaux d'erreur).
Il ne faut pas les appeler directement, tout passe par la fonction `validate`
qui, en fonction du type de modèle, achemine les bonnes erreurs à remonter.
