# Glossaire

## Bank Information

Une `bank information` un composé d'un IBAN et d'un RIB. Il est lié à une `venue` ou un `offerer`.
Il permet de rembourser l'`offerer` par virement SEPA.

## Booking

Un `booking` est fait par un `user` `bénéficiaire` du pass Culture.
Il permet d'accéder à l'`offer` grâce à un `token` qui sera saisi par un `user` pro.

## Deposit

Un `deposit` est crée par les administrateurs du pass Culture afin de créditer le compte 
d'un `user` `bénéficiaire` d'une somme en euros. Cette somme lui permettra ensuite de 
créer des `bookings` sur des `offers` payants.

## Mediation

Une `mediation` a pour but de mettre en valeur une `offer` au sein d'une `recommendation` 
présentée à un `user`. Elle peut contenir du texte et une image.

## Offer

Une `offer` a pour but d'être recommandée aux `users`. Elle est issue d'un `product` du catalogue ou 
est créée par un `user` pro.

## Offerer

Un `offerer` est une personne morale disponsant d'un `siren` et qui a été autorisée par 
les administrateurs du pass Culture à utiliser le portail pro.

## Recommendation

Une `recommendation` est créée pour présenter une `offer` à un `user`, si possible avec une `mediation`.
Elle a pour but d'inciter un `user` à découvrir une `offer` et lui permettre de la réserver s'il le souhaite.

## Stock

Un `stock` représente un nombre de `booking` potentiels sur une `offer` donnée, à un prix donné 
(et des dates s'il l'`offer` porte sur un `product` de type évènement). Lorsqu'un `user` crée 
un `booking`, il le fait sur un `stock`.

## Product

Un `product` représente un objet culturel d'un certain type : un évènement, un bien culturel, un abonnement, etc.

## User

Un `user` peut être de différent type. On parlera de `bénéficiaire` s'il s'agit d'un utilisateur 
de la webapp, d'`acteur culturel` pour un utilisateur du portail pro et enfin d'`admin` 
pour un membre de l'équipe du pass Culture.

## Venue

Une `venue` est un lieu géré par un `offerer` au sein duquel des `offers` sont proposées. Un lieu
peut éventuellement être rattaché à un `siret` correspondant au `siren` de l'`offerer`. Il peut
aussi être virtuel, i.e. en ligne, pour y proposer des `offers` numériques.