POC pagination :

Back :

- ajouter clause order by created_at dans la query get_capped_offers_for_filters
- ajouter deux paramètres page (numéro de la page) et size (taille d'une page) à la route list_offers
- modifier le modele ListOffersQueryModel pour retourner le total des offres, la page actuelle, le nombre d'element, le nb de pages, optionnel (hasPrev et hasNext),
- db.paginate https://flask-sqlalchemy.readthedocs.io/en/stable/api/#module-flask_sqlalchemy.pagination : prend en paramètre la size et la page, et retourne (total, hasPrev, hasNext, pages (nb de pages))

Front :

- faire un appel API changement de page
- utiliser le nouveau composant de pagination..?

Avantages

- facile à mettre en place
- permet d'accéder à toutes les offres
-

Inconvénients
