/**
 *
 * Lancer les tests en local
 * ./node_modules/.bin/testcafe chrome ./testcafe/02_signin.js  --env=local
 *
 */
import { ROOT_PATH } from '../src/utils/config'

fixture('08_01 Booking Card').page(`${ROOT_PATH}connexion`)

// J'accède à une offre
// Je clique sur le bouton fleche/details
// Je peux cliquer sur le bouton j'y vais
// J'ouvre la popup de réservation
// Le calendrier ne s'affiche pas, Si il s'agit d'une offre physique
// Le calendrier s'affiche, Si il ne s'agit pas d'une offre physique
// 25-10_18 Une offre a été réservée, je n'y suis pas allé, l'offre n'est plus disponible. Actuellement, elle apparaît encore dans mes réservations.
