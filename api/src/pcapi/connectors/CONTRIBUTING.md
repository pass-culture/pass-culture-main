# Package `connectors`
Les modules de ce package contiennent des fonctions effectuant des appels à des _web services_ externes au système
d'information du pass Culture.


## Do
Ces fonctions doivent contenir : des appels paramétrés à des _web services_ ainsi que la gestion des _HTTP status codes_
que retournent ces _web services_ et qu'on voudrait éventuellement transformer en exceptions (encapsulation d'erreur).

Par exemple :
```python
def get_by_offerer(offerer: Offerer) -> dict:
    response = requests.get(f"https://api.example.com/{offerer.siren})

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIREN : {}'.format(offerer.siren))

    return response.json()
```

Cf. `src/pcapi/connectors/sirene.py` pour un exemple récent.


## Don't
Ces fonctions sont généralement totalement indépendantes du reste du
code : elles ne doivent pas contenir de règles de gestion, effectuer
des requêtes vers la base de données (hors vérification de *feature
flag*), etc.


## Testing
Ces fonctions sont testées à l'aide de `requests_mock`. Cf. `tests/connectors/sirene_test.py` pour un exemple.
