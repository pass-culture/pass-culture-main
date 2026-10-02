## Résumé

Un paragraphe résumant **ce dont** il est question et **pourquoi** il en est question.

> [!NOTE]
> Autrement dit, le **what** & **why**

Mise en place d'un système asynchroen de réservation aux billetteries externes pour pouvoir gérer les montées en charges.

## Contexte

- Quelle est la situation actuelle ?
- Quel est le problème que l'on est en train de résoudre ?
- Pourquoi s'attaquer à ce problème maintenant ?
- - (si pertinent) Pourquoi limiter le scope de l'ADR ?

Sur le pass Culture, certaines offres sont synchronisées via des partenaires techniques qui sont des fournisseurs de billetterie.
Lorsqu'un utilisateur de l'app clique sur le bouton de confirmation de réservation pour l'une de ces offres, un appel `POST /native/v1/bookings` est effectué. Celui déclenche une prise de verrou sur la table `stock` pour la ligne concernée et la création d'un `Booking` dans notre base de données. Ensuite, un appel HTTP est effectué à l'URL renseignée par le partenaire technique pour la création d'un ticket dans leur système. Le temps d'attente d'une réponse pour ce dernier appel est défini par la variable d'environnement `EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS` (actuellement définie 20s ici). Lors de la réception d'une réponse positive, la réservation est créée dans notre système, au statut `CONFIRMED`, le verrou est relâché et la réponse est envoyée à l'app. Le backend a un maximum de 30s pour répondre, au-delà, l'app reçoit une réponse qui indique un timeout.
Le fonctionnement est analogue pour l'annulation d'une réservation.
Ce système est simple et fonctionne bien quand le partenaire technique répond rapidement.

Le premier problème est que le temps de réaction de l'app est totalement dépendant du temps de réponse du partenaire technique, ce qui peut donner une expérience dégradée à l'utilisateur.
Deuxièmement, l'utilisateur peut appuyer plusieurs fois sur le bouton de réservation, auquel cas c'est autant de requêtes qui seront envoyés au système de billetterie externe. **À vérifier : quelles conséquences dans ce cas ? Je crois qu'il y a un YWH qui exploite ce fonctionnement**
Enfin, un appel HTTP à la billetterie externe bloque le fonctionnement du thread dans lequel il est exécuté, et le temps de ce blocage, le verrou sur le stock est gardé, et la connexion SQL est laissé ouverte. Si de nombreux appels s'accumulent et que les partenaires techniques mettent du temps à répondre, tous les threads de tous les pods disponibles peuvent être bloqués. De plus, le nombre de connexions à la base de données disponibles est limité à 64 (**À vérifier**). Donc il est possible que l'ensemble des connexions soient utilisées pour finalement aucune exécution d'opération, ce qui mettrait à l'arrêt la quasi totalité des opérations du pass Culture : app, portail pro, BO, crons, envois d'emails et notifications, etc., pour un temps indéterminé.

## Priorités, exigences et contraintes (par ordre d'importance)

**:warning: C'est la partie cruciale.**

Listez les éléments essentiels pour la prise de décision par ordre d'importance. Soyez précis (c'est-à-dire clairs et concrets) et donnez des objectifs quantifiables quand cela est possible.

1. **[Nom de la priorité]** - [Pourquoi c'est important ? Est-ce une raison technique ou métier ?]
2. **[Nom de la priorité]** - [Pourquoi c'est important ?]
3. **[Nom de la priorité]** - [Pourquoi c'est important ?]

1. **[Fiabilité]** - [Réduire drastiquement le taux d'erreurs à la réservation pour les utilisateurs de l'app]
2. **[Simplicité d'intégration pour l'app]** - [Le but dans un premier temps est de ne pas modifier l'expérience pour les utilisateurs de l'app ni d'impliquer une refacto pour le code front]
3. **[Observabilité]** - [Collecter des données sur la fiabilité des PT et l'usage de notre système]


> [!NOTE]
> Souvent, si les personnes s'opposent sur les décisions, c'est qu'ils pondèrent les priorités différemment.
> C'est lors de l'explicitation des priorités que se fait la véritable prise de décision.

## Les solutions proposées
### Option A : [Nom de la solution]
Description de la solution

**Pour :**
- ...

**Contre :**
- ...

**Comment cette solution répond aux priorités ?**
Revue de la solution priorité par priorité
1. Nom de la priorité : ...
...

**Effort estimé :** X jours/homme (ou semaines/homme)

**Niveau de risque :** Bas/Moyen/Haut

**(optionnel) Stratégie d'implémentation / Chemin critique :** ...

### Option B: [Nom de la solution]
...

### Option D: la réponse D, i.e. ne rien faire
Il est bon aussi d'envisager les conséquences d'une non-action sur le problème remonté.

## Recommendation (optionnel)
Quelle est la meilleure option selon vous et pourquoi ?

## Parties prenantes
Qui a besoin d'être inclus-e dans la prise de décision ? Tagger les.

## Questions ouvertes
Sur quoi avez-vous besoin d'avoir des informations ?

## Timeline
Quand cette décision doit-elle être prise ? Qu'est-ce qui définit la date butoire ?
