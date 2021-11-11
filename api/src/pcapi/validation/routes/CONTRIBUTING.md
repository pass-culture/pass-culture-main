# Package `validation.routes`

Les modules de ce package contiennent des fonctions **pures**, c'est à dire qui offrent une transparence réferentielle
et qui sont sans effets de bord. Elles ont pour but de garantir la cohérence des données reçues en entrée des routes d'API ;
c'est à dire de permettre aux fonctions de _routing_ de décider si un _request body_ ou des _URL query parameters_ sont utilisables.

## Do

Ces fonctions doivent contenir : des vérifications d'intégrité des données passées en paramètre et des éventuelles levées
d'exceptions pour signaler un problème.

Par exemple :

```python
def check_event_occurrence_offerer_exists(offerer):
    if offerer is None:
        api_errors = ApiErrors()
        api_errors.add_error('eventOccurrenceId', 'l’offreur associé à cet évènement est inconnu')
        raise api_errors
```

Si ces validations sont utilisées dans les routes et génèrent des exceptions et des codes réponses api,
il est préférable d'utiliser les classes d'erreurs existantes en customisant la réponse si nécessaire.

Par exemple :

```python
def check_api_key_allows_to_validate_booking(valid_api_key: ApiKey, offerer_id: int):
    if not valid_api_key.offererId == offerer_id:
        api_errors = ForbiddenError()
        api_errors.add_error('user', 'Vous n’avez pas les droits suffisants pour valider cette contremarque.')
        raise api_errors
```

## Don't

Ces fonctions ne doivent pas contenir : des règles de gestion, des _queries_ vers la base de données ou des appels à des
web services.

## Testing

Ces fonctions sont testées de manière unitaire et ne nécessitent ni _mocking_, ni instanciation de la base de données
ou d'un contexte Flask. Ces tests doivent être extrêmement rapides à l'exécution et sont généralement un excellent
terrain d'apprentissage pour le Test Driven Development (TDD).

Ils ont pour objectif de :

* Lister les comportements et responsabilités d'une fonction ;
* Lister les exceptions relatives à la cohérence des données ;
* Donner des exemples d'exécution d'une fonction.

Par exemple :

```python
def test_check_valid_signup_raises_api_error_if_not_contact_ok():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@example.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']
```

Utiliser le try/except pour les cas passants :

Par exemple :

```python
def test_does_not_raise_error_when_user_is_authenticated(self, app):
    # Given
    user = User()
    user.is_authenticated = True
    email = 'fake@example.com'

    # When
    try:
        check_user_is_logged_in_or_email_is_provided(user, email)

    # Then
    except:
        assert False
```
