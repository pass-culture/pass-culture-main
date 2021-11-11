# Package `models`

Les modules de ce package contiennent principalement des classes qui implémentent le modèle de données relationnel du
backend pass Culture. Ces classes peuvent représenter :

- des tables SQL (héritage depuis `PcOject` et `Model`) ;
- des colonnes de tables SQL (on parle alors de classe `*Mixin`).

Ce système repose entièrement sur l'ORM SQL `Alchemy`.

## Do

Les modifications apportées au modèle de données doivent impérativement et systématiquement être scriptées dans une
migration de schéma relationnel avec `Alembic`. Les deux modifications (classes d'ORM et migration `Alembic`)
doivent être mergée simultanément dans la branche master.
Il est impératif d'être ISO entre une classe ORM et la révision `Alembic` car la production ne joue que les révisions
`Alembic` et ne s'occupe pas des `Model`.
Il est important de savoir qu'une clé étrangère n'est pas un index par défaut en `Postgres`, il faut donc
le rajouter en fonction de votre contexte.

Donc quand on a :

```python
criterionId = Column(BigInteger,
    ForeignKey('criterion.id'),
    index=True)
```

Il faut dans la révision `Alembic` :

```python
ALTER TABLE ONLY offer_criterion ADD CONSTRAINT "offer_criterion_criterionId_fkey" FOREIGN KEY ("criterionId") REFERENCES criterion(id);
CREATE INDEX "idx_offer_criterion_criterionId" ON offer_criterion ("criterionId");
```

## Testing

Les classes présentes dans ce package ne sont pas testables puisque composées, dans leur forme la plus simple, uniquement
de déclaration de champs. Toutefois, si on souhaite leur donner des comportements ou de la logique (e.g. via des méthodes
d'instance ou des _properties_) il est possible de les tester unitairement.

Par exemple :

```python
def test_date_range_matches_the_occurrence_if_only_one_occurrence():
    # given
    offer = Offer()
    offer.product = Product()
    offer.eventOccurrences = [
        create_event_occurrence(offer, beginning_datetime=two_days_ago)
    ]

    # then
    assert offer.dateRange == DateTimes(two_days_ago, five_days_from_now)
```

## Pour en savoir plus

- https://fr.wikipedia.org/wiki/Mapping_objet-relationnel
- https://www.sqlalchemy.org/features.html
- https://alembic.sqlalchemy.org/en/latest/index.html
