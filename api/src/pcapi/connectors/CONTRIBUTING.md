# Package `connectors`
Les modules de ce package contiennent des fonctions effectuant des appels à des _web services_ externes au système
d'information du pass Culture.

## Do
Ces fonctions doivent contenir : des appels paramétrés à des _web services_ ainsi que la gestion des _HTTP status codes_
que retournent ces _web services_ et qu'on voudrait éventuellement transformer en exceptions (encapsulation d'erreur).

Par exemple :
```python
def get_by_offerer(offerer: Offerer) -> dict:
    response = requests.get("https://sirene.entreprise.api.gouv.fr/v1/siren/" + offerer.siren, verify=False)

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIREN : {}'.format(offerer.siren))

    return response.json()
```

## Don't
Ces fonctions ne doivent pas contenir : des règles de gestion (qui appartiennent au `domain`), des _queries_ vers la
base de données une quelconque notion liée au _routing_ de l'API du pas Culture.

## Testing
Ces fonctions sont testées de manière unitaire mais en coupant la dépendance vers le _web service_ : on utilise un mécanisme
de _mocking_. Ce qui est donc testé n'est pas réellement l'appel au service, mais le comportement de notre code si le service
renvoie une erreur, un réponse valide, etc.

Par exemple :
```python
@patch('pcapi.connectors.api_entreprises.requests.get')
def test_write_object_validation_email_raises_ApiEntrepriseException_when_siren_api_does_not_respond(requests_get):
    # Given
    requests_get.return_value = MagicMock(status_code=400)
    validation_token = secrets.token_urlsafe(20)

    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    #When
    with pytest.raises(ApiEntrepriseException) as error:
        get_by_offerer(offerer)

    #Then
    assert 'Error getting API entreprise DATA for SIREN' in str(error)
```

## Pour en savoir plus
https://docs.python.org/3.6/library/unittest.mock.html
