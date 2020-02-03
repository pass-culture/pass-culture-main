# Validation des données

On utilise trois niveaux de validation des données entrantes.

1. Au niveau des routes, on utilise des fonctions de validation, regroupées dans le package `validation` ;
2. Au niveau des modèles SQLAlchemy, dans les méthodes `errors` ;
3. Au niveau de PostgreSQL, avec des `constraints` et des `triggers`.

Les critères utilisés pour définir à quel niveau il faut placer des règles de validation sont :

1. On utilisera `validation.routes` :
    - lorsqu'on cherche à éviter les usages malveillants, par exemple pour accéder à la liste de réservations d'un autre offreur ;
    - si on a besoin de renvoyer des status HTTP précis (autre que 200, 400) ;
    - lorsque les règles de validation sont spécifiques à une seule route.

2. On utilisera `validation.models` :
    - Lorsque la règle de validation est partagée par plusieurs points d'entrée (route API, script) ;
    - Lorsqu'on souhaite que certaines conditions soient respectées lors des opérations manuelles effectuées via l'ORM pour assurer la cohérence de nos données ;
        - exemple : tentative d'enregistrement d'un lieu avec un siret non conforme (dont les premiers chiffres ne correspondent pas au siren).

3. On utilisera les `constraints` et `triggers` :
    - Si avoir les données incohérentes met en péril la continuité du service ;
    - Si avoir des données incohérentes met en péril des règles métier critiques. Exemples : on ne peut pas réserver si on n'a pas de crédit, on ne peut pas réserver si on n'a pas de stock ;
    - Si une violation des règles métier concernées implique des mesures exceptionnelles (restauration d'un backup de production, requête SQL complexe pour corriger).
