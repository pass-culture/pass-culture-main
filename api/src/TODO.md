# Mutualisations des calls aux 3rd parties

## L'event 'user deposit activated'

[x] Créer un package events
[ ] Créer une fonction qui dispatche l'event 'user deposit activated'

Backends :
[ ] Push notification
[x] SMS
[ ] Email
[x] Amplitude
[ ] InternalNotification

# Plan de l'aprem

[ ] TDD 'user deposit activated'

# Étapes suivantes

[ ] Envoi des évènements via le package `tasks` (passage en asynchrone du coup)
[ ] Refacto des tests de dispatch suite au point précédent
[ ] Définition des évènements concernés (les transactionnels et màj des users semblent difficiles à refacto, ex : BOOKING_CANCELLED)
[ ] Implémentation dans la package `tasks` des serializers manquant
