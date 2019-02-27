# Package `models`
Les modules de ce package contiennent principalement des classes qui implémentent le modèle de données relationnel du
backend pass Culture. Ces classes peuvent représenter :
* des tables SQL (héritage depuis `PcOject` et `Model`)
* des colonnes de tables SQL (on parle alors de classe `*Mixin`)

Ce système repose entièrement sur l'ORM SQL Alchemy.

## Do
Les modifications apportées au modèle de données doivent impérativement et systématiquement être scriptées dans une
migration de schéma relationnel avec Alembic. Les deux modifications (classes d'ORM et migration Alembic) doivent être
merged simultanément dans la branche master.

## Testing
Les classes présentes dans ce package ne sont pas testables puisque composées, dans leur forme la plus simple, uniquement
de déclaration de champs. Toutefois, si on souhaite leur donner des comportements ou de la logique (e.g. via des méthodes
d'instance ou des _properties_) il est possible de les tester unitairement.

Par exemple :
```python
@pytest.mark.standalone
def test_date_range_matches_the_occurrence_if_only_one_occurrence():
    # given
    offer = Offer()
    offer.event = Event()
    offer.eventOccurrences = [
        create_event_occurrence(offer, beginning_datetime=two_days_ago, end_datetime=five_days_from_now)
    ]

    # then
    assert offer.dateRange == DateTimes(two_days_ago, five_days_from_now)
```

## Pour en savoir plus
* https://fr.wikipedia.org/wiki/Mapping_objet-relationnel
* https://www.sqlalchemy.org/features.html
* https://alembic.sqlalchemy.org/en/latest/index.html