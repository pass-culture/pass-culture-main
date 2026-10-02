Proposition d'amélioration de la réservation d'offres.

## Contexte
Le type d'offre "externe" désigne les offres pour lesquelles on a besoin de contacter un service de billeterie exerne via une API web pour pouvoir valider la réservation.
Le processus de réservation d'offre en générale repose sur la création de "Booking" dans la bdd et suit un système d'états pour décrire leur validité et le suivi de leur remboursement à l'AC.
On crée une réservation et on considère qu'elle est automatiquement confirmée en se basant sur une "machine à états" basé sur les états suivants: `CONFIRMED`, `USED`, `CANCELLED`, `PENDING_REIMBURSEMENT`, `REIMBURSED`. Cela ne pose pas de problème dans la grande majorité des sauf pour les offres externe, parce que lorsque la route de création est appelée on procède à la création d'une entrée Booking (sans commit) dans la bdd ensuite on appel l'API externe pour obtenir leur retour. Cela est problèmatique pour les raisons suivantes:
1. Le blocage d'un pod web le temps qu'on ait une réponse du serveur distant → le nombre de pods est limité et au bout d'un certain nombre on n'a plus d'instance web pour répondre à toutes les requêtes et plein d'utilisateurs ont une app qui leur affiche des erreurs de connexion
2. Pour chaque thread web bloqué, une connexion à la bdd est en attente → le nombre de connexions à la bdd est limité et nouvelle tâches/requêtes ne peuvent plus ouvrir de nouvelle connexion à la bdd
3. Un certain nombre de fournisseurs de billet ont une API web qui fonctionne en asynchronne et on peut avoir des retours positifs intermédiaires juste avant de confirmer la non-réservation de l'offre -> on aura des données corrompues dans la bdd qui ne donnent pas forcément droit à de vraies réservation
4. La création de réservation dépend du temps de réponse d'un serveur distant. Si l'utilisateur envoie une première demande de réservation, une première réservation est envoyé à la billeterie externe. Ensuite si le serveur tarde à répondre, l'utilsateur peut envoyer une 2ème demande de réservation et on aura 2 réservations créées auprès de leur service et probablement une seule de confirmée dans notre bdd

## Proposition

On a besoin de changer la façon dont sont créées les réservations pour pouvoir supporter la montée en charge et se débarrasser de la dépendance aux service tiers de billeterie. Il faut pouvoir créer des réservations sans qu'elles soient directement confirmées et avoir des états intérmédiaires.
Voici les étapes qui nous permetteront d'atteindre notre objectif :
1. Ajout de nouveaux états intermédiaires :
   - "INITIATED" désignant la création de la résa sans prélèvement du crédit jeune
   - "PENDING_CONFIRMATION" désignant la création de la résa avec prélèvement du crédit jeune
   - "PENDING_CANCELLATION" désignant qu'une demande d'annulation a été envoyée au service distant sans remboursement du crédit jeune
2. Modifier la route de réservation pour ne faire qu'ajouter une entrée dans la table Booking pour préréserver en mettant l'état `PENDING_CONFIRMATION`
3. Déplacer la partie d'appel au service externe dans une tâche celery qui sera traîté en asynchronne
4. Faire de même avec la partie annulation pour être sûre que le service externe
5. Mettre à jour le calcule du crédit du jeune pour prendre en compte les nouveaux états
6. Vérifier la partie finance pour s'assurer que la valorisation reste indépendante des nouveaux états
7. Mettre à jour l'app native pour s'assurer de l'affichage des réservations en attente de confirmation
8. Mettre à jour le Backoffice et le Portail pro pour la gestion de l'affichage des nouveaux états des réservations