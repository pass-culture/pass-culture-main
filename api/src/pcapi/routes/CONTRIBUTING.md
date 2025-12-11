# Package `routes`

Les modules de ce package contiennent :
- des fichiers définissant les contrôleurs des routes : `routes/*/endpoints/*.py`
- des fichiers définissant les modèles d'entrée et sortie des routes : `routes/*/serialization/*.py`

## Standards

Le contrôleurs peuvent contenir : des appels à des fontions de `api`, `connectors` ou `repository`.

On utilise la librairie `pydantic` pour sérialiser les données.

```python
@blueprint.native_v1.route("/me", methods=["GET"])
@spectree_serialize(
    response_model=serializers.UserProfileResponse,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_user_profile() -> serializers.UserProfileResponse:
    return serializers.UserProfileResponse.from_orm(current_user)

```


### Tests

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

Pour chaque route, ajouter une classe de tests. Les sous-méthodes testent les différents cas souhaité.

```python
class GetRoute:
    @pytest.mark.usefixtures("db_session")
    def test_offers_are_paginated_by_chunks_of_10(self, client, app):
        user = UserFactory()
        offer = OfferFactory(user, 20)

        response = client.with_session_auth(email='user@test.com').get('/offers')

        assert response.status_code == 200
        assert len(response.json()) == 10
```

# Troubleshooting

## Ajout d'un nouveau fichier de route

Pour que les routes d'un nouveau fichier de routes soient exposées, il faut bien s'assurer que ce fichier soit initialisé dans le fichier `__init__.py` situé au même niveau dans l'arborescence de fichiers, jusqu'au fichier `__init__.py` du package `pcapi.routes`.
