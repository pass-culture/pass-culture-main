# Package `domain`
Les modules de ce package contiennent des fonctions de deux natures différentes :
* cas n°1 : ce sont des fonctions **pures**, c'est à dire qui offrent une transparence réferentielle
* cas n°2 : ce sont des fonctions **impures**, qui font appel à des fonctions de `connectors` ou `repository` passées
en paramètre (`arg` ou `kwarg`)

C'est à dire que pour deux appels avec les mêmes valeurs retournées par les fonctions de `connectors` ou `repository`,
les fonctions de `domain` doivent retourner les mêmes resultats.

Elles ont toujours pour but d'implémenter des règles de gestion qui modélisent le "domaine métier" du pass Culture.

## Do
Ces fonctions doivent contenir : des appels à des fontions de `domain`, `connectors` ou `repository` ainsi que
les différents _HTTP status codes_ que l'ont souhaite retourner.

Par exemple :
```python
def get_expenses(bookings: List[Booking]) -> dict:
    total_expenses = _compute_booking_expenses(bookings)
    physical_expenses = _compute_booking_expenses(bookings, _get_bookings_of_physical_things)
    digital_expenses = _compute_booking_expenses(bookings, _get_bookings_of_digital_things)

    return {
        'all': {'max': SUBVENTION_TOTAL, 'actual': total_expenses},
        'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': physical_expenses},
        'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': digital_expenses}
    }
```

## Don't
Ces fonctions ne doivent pas contenir : des _queries_ vers la base de données, des appels à des web services, ou quoi que
ce soit qui soit considéré comme un I/O. Ces `I/O functions` peuvent être utilisées par une `domain function` à condition
qu'elles soient proprement injectées (i.e. en argument de fonction, en keyword-argument de fonction ou en constructeur de classe).

Par exemple :
```python
def create_initial_deposit(user_to_activate):
    existing_deposits = Deposit.query.filter_by(userId=user_to_activate.id).all()
    if existing_deposits:
        error = AlreadyActivatedException()
        error.add_error('user', 'Cet utilisateur a déjà crédité son pass Culture')
        raise error

    else:
        deposit = Deposit()
        deposit.amount = 500
        deposit.user = user_to_activate
        deposit.source = 'activation'
        return deposit
```

## Testing
Ces fonctions sont testées de manière unitaire et ne nécessitent ni _mocking_, ni instanciation de la base de donnée
ou d'un contexte Flask. Ces tests doivent être extrêmement rapides à l'exécution et sont généralement un excellent terrain
d'apprentissage pour le Test Driven Development (TDD).

Ils ont pour objectif de :
* lister les comportements et responsabilités d'une fonction
* lister les exceptions "métier" qu'une fonction est susceptible de lever
* donner des exemples d'exécution d'une fonction

Par exemple :
```python
class DigitalThingsReimbursementTest:
    def test_apply_for_booking_returns_a_reimbursed_amount(self):
        # given
        booking = create_booking_for_thing(url='http://', amount=40, quantity=3)

        # when
        reimbursed_amount = ReimbursementRules.DIGITAL_THINGS.value.apply(booking)

        # then
        assert reimbursed_amount == 0
```

## Pour en savoir plus
* https://fr.wikipedia.org/wiki/Transparence_r%C3%A9f%C3%A9rentielle
* On appelle une `I/O function` toute fonction qui dépend d'un système externe à son contexte d'exécution. Par exemple :
  * un système de fichier
  * une base de donnée
  * l'horloge du serveur
  * le réseau
  * un capteur de luminosité
  * etc.
