import getDepartementByCode from '../../../../utils/getDepartementByCode'

export const getRemainingCreditForGivenCreditLimit = walletBalance => ({
  actual: expenses,
  max: creditLimit,
}) => {
  const absoluteRemainingCredit = creditLimit - expenses
  const remainingCredit = Math.min(walletBalance, absoluteRemainingCredit)
  return remainingCredit
}

export const getDepartment = departmentCode => {
  const departmentName = getDepartementByCode(departmentCode)
  return `${departmentName} (${departmentCode})`
}

export const getAccountDeletionEmail = (userId, userEmail) => {
  const supportEmailAddress = 'support@passculture.app'
  const emailSubject = 'Suppression de mon compte pass Culture'
  const emailBody = `Bonjour,

Je vous écris afin de vous demander la suppression de mon compte pass Culture n°${userId}, associé à l’adresse mail ${userEmail}.

J'ai conscience que la suppression de mon compte entraînera l'annulation définitive de l'ensemble de mes réservations en cours.

J'ai 30 jours pour me rétracter. Au-delà de ce délai, je ne pourrai plus accéder à mon compte pass Culture, ni au crédit éventuellement restant.

Bien cordialement,`

  return encodeURI(`mailto:${supportEmailAddress}?subject=${emailSubject}&body=${emailBody}`)
}
