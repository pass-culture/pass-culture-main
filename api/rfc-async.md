## Résumé

Mise en place d'un système asynchrone de réservation (et d'annulation) auprès des billetteries externes, afin d'absorber les pics de charge, les latences et les erreurs des partenaires techniques (PT) sans dégrader l'expérience des jeunes ni la stabilité de la plateforme.

## Contexte

Sur le pass Culture, certaines offres sont synchronisées via des partenaires techniques qui fournissent la billetterie.

Lorsqu'un utilisateur de l'app clique sur le bouton de confirmation de réservation pour l'une de ces offres, un appel `POST /native/v1/bookings` est effectué. Il déclenche :

1. une prise de verrou (`FOR UPDATE`) sur les lignes concernées des tables `stock` et `user` ;
2. la création d'un `Booking` dans notre base de données ;
3. un appel HTTP synchrone à l'URL renseignée par le PT, pour créer un ticket dans son système. Le temps d'attente de la réponse est défini par la variable d'environnement `EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS` (actuellement définie 20s [ici](https://github.com/pass-culture/infra/blob/a334ba56c5bda4045659c6994d2921167889d2ad/layers/pcapi/deployments/prd/values.yaml#L339)).

À la réception d'une réponse positive, la réservation est enregistrée au statut `CONFIRMED`, le verrou est relâché et la réponse est renvoyée à l'app. Le backend dispose d'au maximum 30 s pour répondre, au-delà, l'app reçoit un timeout.

L'annulation fonctionne de manière analogue.

Ce fonctionnement est simple et convient tant que le PT répond rapidement. Il pose cependant plusieurs problèmes :

- **Dépendance au PT** : le temps de réaction de l'app dépend entièrement du temps de réponse du PT, ce qui dégrade l'expérience de l'utilisateur.
- **Requêtes multiples** : un utilisateur peut, en les forgeant (avec `curl`, par exemple), envoyer plusieurs demandes de réservation simultanées. Chacune est transmise à la billetterie externe, ce qui peut créer plusieurs tickets chez le PT alors qu'aucune réservation n'est créée chez nous.
- **Saturation des ressources** : l'appel HTTP bloque le thread qui l'exécute. Pendant ce temps, le verrou sur le stock est conservé, la transaction SQL reste ouverte et la connexion à la base ne peut servir à rien d'autre. Si les appels s'accumulent et que les PT tardent à répondre, tous les threads de tous les pods peuvent être bloqués. Le nombre de connexions à la base étant limité, elles peuvent toutes être consommées sans qu'aucune opération n'aboutisse, ce qui mettrait à l'arrêt la quasi-totalité des services du pass Culture (app, portail pro, BO, crons, etc.) pour une durée indéterminée (cf : incident "Spideman").

## Priorités, exigences et contraintes (par ordre d'importance)

1. **[Résilience :]** Réduire le taux d'erreurs sur `POST /bookings`.
   Les taux d'erreurs sur les réservations aux billetteries externes dépassaient 6 % en mai-juin pour les réservations et 15 % pour les annulations ([tableau](https://docs.google.com/spreadsheets/d/1Fq3466gj88hi0wT55rcBSw8cB7_zizp6PRDGJm8FYBc/edit?gid=0#gid=0)).
   Le but est que ces erreurs ne se répercutent pas sur les réponses à la route `POST /bookings`, pour laquelle on veut viser un taux d'erreur (4xx/5xx) quasi-nul.
   _Proposition :_ fixer un objectif chiffré (ex. : 0 timeout et 0 `5xx` imputable à un PT sur cette route ; verrou sur `stock` relâché avant tout appel externe, quelle que soit la latence du PT).
2. **[Observabilité :]** Collecter des données sur les PT : trafic, latences, erreurs, statut.
   Nous ne disposons aujourd'hui que d'un [dashboard Grafana](https://monitoring.prd.infra.passculture.team/goto/23MTIxjvg?orgId=1) donnant la répartition des codes de retour de `POST /bookings`, sans possbilité de classer par PT. De plus, dans l'attente de réponses nous sommes aveugles.
   L'objectif est de pouvoir récolter des données sans avoir à fouiller les logs et éventuellement alerter.
3. **[Fiabilité :]** L'état de la base de données reflète la réalité des événements.
   Aujourd'hui, aucune trace en base n'indique qu'une tentative de réservation a eu lieu, et des réservations sont mises à `CONFIRMED` alors qu'elles ne le sont pas encore côté PT.
4. **[Simplicité d'intégration pour l'app]** Dans un premier temps, ne pas modifier l'expérience des utilisateurs ni imposer de refonte du code front.
   D'autres chantiers UX et code sont prévus et sont hors du périmètre de ce RFC.

## Les solutions proposées

### Option A : traiter uniquement les réservations externes via des tâches Celery

- Les réservations qui ne passent pas par une billetterie externe (« internes ») restent traitées de manière synchrone, avec le fonctionnement actuel : création au statut `CONFIRMED`, puis `USED` pour les `AUTOMATICALLY_USED_SUBCATEGORIES` ou après validation de la contremarque.
- L'app choisit elle-même la route qu'elle appelle : le chemin asynchrone est exposé via une route dédiée, et `POST /native/v1/bookings` conserve son comportement synchrone actuel pour les anciennes versions.
- Les réservations externes sont créées immédiatement au statut `PENDING_CONFIRMATION` et leur traitement est délégué à une tâche Celery placée dans une file prioritaire dédiée.
- Le stock est décrémenté à la création du `Booking` (pas de survente) et la réservation compte immédiatement dans le calcul du crédit du jeune. Le verrou sur `stock` et `user` n'est tenu que le temps de cette création et est relâché avant tout appel HTTP.
- La tâche passe le `Booking` à `CONFIRMED` en cas de succès, ou à `FAILED` en cas d'échec définitif auquel cas le stock et le crédit sont restitués.
- Les effets de bord actuellement déclenchés à la fin de `book_offer` (emails bénéficiaire et pro, événement de tracking, notification à la billetterie, indexation, mise à jour Batch/external user) sont déplacés dans la tâche, après le passage à `CONFIRMED`.
- Annulation : la réservation passe à `PENDING_CANCELLATION` avant traitement et continue de compter dans le crédit tant que l'opération n'a pas réussi, elle passe ensuite à `CANCELLED` et le crédit est libéré. En cas d'échec, elle reste en `PENDING_CANCELLATION` : la tâche est retentée et le cron de rattrapage la reprend, avec une alerte si elle reste bloquée trop longtemps.
- (Bonus) Cron de rattrapage pour les réservations restées trop longtemps en `PENDING_CONFIRMATION` ou `PENDING_CANCELLATION` (tâche perdue, worker redémarré, etc.).

**Pour :**

- Indépendance vis-à-vis des temps de réponse des PT : la latence de `POST /bookings` devient courte et bornée.
- Plus aucun thread web ni connexion SQL n'est immobilisé pendant un appel externe : le risque de saturation des pods et du pool de connexions disparaît.
- Meilleure résilience aux montées en charge : plusieurs réservations d'un même stock peuvent être traitées en parallèle.
- Permet d'intégrer des billetteries dont les temps de réponse dépassent notre timeout (Secutix).
- Tire parti des retries de Celery.
- Le dashboard Grafana de monitoring des tâches Celery existe déjà ((ici)[https://monitoring.prd.infra.passculture.team/goto/olE6KfCDR?orgId=1]).

**Contre :**

- Le délai de confirmation de la réservation s'allonge pour le bénéficiaire.
- Il faut implémenter un polling côté app. Une route asynchrone dédiée évite de changer le contrat de `POST /bookings` : les anciennes versions continuent d'utiliser le chemin synchrone, qu'il faut donc maintenir pendant la transition.
- Nouveaux statuts à gérer partout où un `Booking` est lu (« mes réservations », crédit, stats, BO, portail pro, exports, emails, crons). Un `Booking` non final ne doit pas être traité comme confirmé (email, QR code/contremarque).
- Dépendance renforcée à Celery et à son broker pour un parcours critique.
- Les requêtes multiples d'un même utilisateur ne sont pas résolues en elles-mêmes : sans contrainte d'unicité ou rate limiting, chaque `POST` crée un `Booking` et une tâche.
- L'utilisateur n'est informé d'un échec qu'après coup.

**Comment cette solution répond aux priorités ?**

1. Résilience : la latence et les erreurs de `POST /bookings` ne dépendent plus d'acteurs externes : les erreurs des PT deviennent des statuts `FAILED` traités de manière asynchrone.
2. Observabilité : monitoring des tâches Celery (durée, échecs, retries, taille de la file) alimentées par les transitions de statut.
3. Fiabilité : les statuts des réservations suivent entièrement le flux réel de l'opération.
4. Simplicité d'intégration pour l'app : le changement se limite à appeler la nouvelle route puis à poller `GET /bookings/<booking_id>` jusqu'à un statut final, avec un nouvel état d'erreur. Ce n'est pas un « zéro changement », mais il reste minime.

**Effort estimé :** 8 semaines/dev

**Niveau de risque :** Moyen
Principaux risques : propagation des nouveaux statuts, réservations et annulations bloquées.

**Stratégie d'implémentation / chemin critique :**

1. Backend : nouveaux statuts (migration + audit des usages de `BookingStatus`), tâche Celery, file dédiée et prioritaire, restitution du stock et du crédit en `FAILED`, cron de rattrapage.
2. Observabilité (en parallèle) : métriques et logs, dashboard et alertes.
3. Route asynchrone dédiée, l'app choisit la route à appeler.
4. App : appel de la nouvelle route, polling, gestion de `FAILED` et du dépassement de délai.
5. Suppression du chemin synchrone à la prochaine mise à jour forcée de l'app.

### Option D : ne rien faire (statu quo)

Les taux d'erreurs actuels ne sont pas acceptables. Ne rien faire revient à rester exposé à des situations comme « l'incident Spiderman », et nous empêche de nous intégrer avec des billetteries qui ne garantissent pas une réponse dans un délai inférieur à notre propre timeout, ce qui est aujourd'hui un enjeu fort pour le pass Culture.

## Recommandation

L'option A.

## Parties prenantes

- Squad conversion (porteuse du chantier, OKR T4 2026)
- Infra (dimensionnement Celery et broker, pool de connexions)
- Data / BO / portail pro (impact des nouveaux statuts)

## Questions ouvertes

- Requêtes multiples : contrainte d'unicité (un `Booking` actif par utilisateur et par stock), rate limiting, ou clé d'idempotence fournie par l'app ?
- Réservations bloquées : quel délai déclenche le rattrapage ?
- Que voit l'utilisateur en cas de `FAILED` ? Faut-il le notifier s'il a quitté l'app ?
- Dimensionnement : capacité des workers Celery, limite de concurrence chez les PT.

## Timeline

Décision attendue d'ici début novembre:

- ce chantier est un des OKRs de la squad conversion pour le T4 2026 ;
- il y a un enjeu de synchronisation avec certains acteurs culturels majeurs au sujet de l'intégration de la billetterie Secutix, dont les temps de réponse sont aujourd'hui inacceptables pour notre système en l'état.
