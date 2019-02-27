# Package `repository`
Les modules de ce package contiennent des fonctions qui implémentent des _queries_ SQL Alchemy basées sur les _Models_
SQL Alchemy définis dans le package `models` ou de la lecture de variables d'environnement (l'environnement étant une
dépendance externe au système).

## Do
Ces fonctions doivent contenir uniquement des requêtes vers la base de donnée qui retournent soit des tuples de données
"primitives" (e.g. une liste d'adresses email), soit des instances de modèles SQL Alchemy. On pourra aussi avoir des
fonctions qui retournent des "morceaux" de queries, c'est à dire des fonctions qui construisent de queries qui ne sont
pas déclenchées (i.e. qui n'ont pas de `.all()` ou `.first()`).
On utilisera des indications de type dans les signatures des fonctions pour indiquer quelles sont les données attendues
en entrée et en sortie.

Par exemple :
```python
def get_by_offer_id(offer_id: int) -> Optional[Offerer]:
    return Offerer.query
        .join(Venue) \
        .join(Offer) \
        .filter_by(id=offer_id) \
        .first()
```

## Don't
Ces fonctions ne doivent pas contenir : des notions relatives au `routing` (e.g. _status codes_ HTTP, verbes HTTP),
des règles de gestion, des appels à des web services.

## Testing
Ces fonctions sont testées dans un contexte Flask, donc avec une connection à la base de données. On considère que ce sont
des tests d'intégration. Ces tests déclenchent donc de vraies requêtes SQL et nécessitent que des données soient présentes en base.
Ces tests utilisent le décorateur `@clean_database` qui s'occupe de vider chaque table avant l'exécution d'un test et insèrent
les données nécessaires dans leur partie `# given`.

Ils ont pour objectif de :
* vérifier qu'une requête fait bien ce qu'elle dit et retourne des données censées
* vérifier que les requêtes gèrent bien les cas aux limites via des exceptions attendues

Par exemple :
```python
@pytest.mark.standalone
class FindUserActivationBookingTest:
    @clean_database
    def test_returns_true_is_a_booking_exists_on_such_stock(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789', name='pass Culture')
        venue_online = create_venue(offerer, siret=None, is_virtual=True)
        activation_offer = create_thing_offer(venue_online, thing_type=ThingType.ACTIVATION)
        activation_stock = create_stock_from_offer(activation_offer, available=200, price=0)
        activation_booking = create_booking(user, stock=activation_stock, venue=venue_online)
        PcObject.check_and_save(activation_booking)

        # when
        booking = find_user_activation_booking(user)

        # then
        assert booking == activation_booking
```

## Pour en savoir plus
* http://flask-sqlalchemy.pocoo.org/2.3/queries/
