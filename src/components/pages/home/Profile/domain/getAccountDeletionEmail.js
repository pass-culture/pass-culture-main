import { SUPPORT_EMAIL } from '../../../../../utils/config'

export const getAccountDeletionEmail = userEmail => {
  const emailSubject = 'Suppression de mon compte pass Culture'
  const emailBody = `Bonjour,

Je vous écris afin de vous demander la suppression de mon compte pass Culture associé à l’adresse e-mail ${userEmail}.

J'ai conscience que la suppression de mon compte entraînera l'annulation définitive de l'ensemble de mes réservations en cours.

J'ai 30 jours pour me rétracter. Au-delà de ce délai, je ne pourrai plus accéder à mon compte pass Culture, ni au crédit éventuellement restant.

Bien cordialement,`

  return encodeURI(`mailto:${SUPPORT_EMAIL}?subject=${emailSubject}&body=${emailBody}`)
}
