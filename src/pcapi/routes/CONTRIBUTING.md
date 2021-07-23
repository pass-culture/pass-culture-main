# Package `routes`

Les modules de ce package contiennent des fonctions python de type _controller_ ainsi que le _binding_ de ces fonctions
avec les routes d'API grâce au _framework Flask_.

## Do

Ces fonctions doivent contenir : des appels à des fontions de `domain`, `connectors` ou `repository` ainsi que
les différents _HTTP status codes_ que l'ont souhaite retourner.

Par exemple :

```python
@private_api.route("/users/current", methods=["GET"])
@login_required
def get_profile():
    user = as_dict(current_user, includes=USER_INCLUDES)
    user['expenses'] = get_expenses(current_user.userBookings)
    return jsonify(user), 200
```

## Don't

Ces fonctions ne doivent pas contenir : des règles de gestion, des _queries_ vers la base de données ou des appels à des
web services.

Par exemple :

```python
@private_api.route('/eventOccurrences', methods=['POST'])
@login_required
@expect_json_data
def create_event_occurrence():
    product = Product.query \
        .join(Offer) \
        .filter(Offer.id == dehumanize(request.json['offerId'])) \
        .first_or_404()

    occurrence = EventOccurrence(from_dict=request.json)
    repository.save(occurrence)
    return jsonify(as_dict(occurrence, includes=EVENT_OCCURRENCE_INCLUDES)), 201
```

## Testing

Ces fonctions sont testées au travers des routes, avec des tests fonctionnels. Ces tests utilisent des appels HTTP et
se positionnent donc "du point de vue du client".

Ils ont pour objectif de :

- documenter les différents status codes qui existent pour chaque route
- documenter le JSON attendu en entrée pour chaque route
- documenter le JSON attendu en sortie pour chaque route
- détecter les régressions sur les routes d'API

Ils n'ont pas pour objectifs de :

- tester l'intégralité des cas passants ou non-passants possibles. Ces cas là seront testés plus près du code, dans des
  modules de `domain` ou de `repository` par exemple.

Par exemple :

```python
class Get:
    class Returns200:
        @clean_database
        def test_offers_are_paginated_by_chunks_of_10(self, app):
            # Given
            user = UserFactory()
            offer = OfferFactory(user, 20)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email='user@test.com') \
                .get('/offers')

            # then
            assert response.status_code == 200
            assert len(response.json()) == 10
```

## Pour en savoir plus

- http://flask.pocoo.org/docs/1.0/quickstart/#routing
