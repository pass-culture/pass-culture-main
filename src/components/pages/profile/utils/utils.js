export const getRemainingCreditForGivenCreditLimit = walletBalance => ({
  actual: expenses,
  max: creditLimit,
}) => {
  const absoluteRemainingCredit = creditLimit - expenses
  const remainingCredit = Math.min(walletBalance, absoluteRemainingCredit)
  return remainingCredit
}

export const getAccountDeletionEmail = (userId, userEmail) => {
  const supportEmailAddress = 'support@passculture.app'
  const emailSubject = 'Suppression%20de%20mon%20compte%20pass%20Culture'
  const emailBody =
    'Bonjour%2C%0D%0A%0D%0AJe%20vous%20%C3%A9cris%20afin%20de%20vous%20demander%20la%20suppression%20de%20mon%20compte%20pass%20Culture%20n%C2%B0' +
    userId +
    '%20associ%C3%A9%20%C3%A0%20l%E2%80%99adresse%20mail%20' +
    userEmail +
    '.%0D%0A%0D%0AJ%27ai%20conscience%20que%20la%20suppression%20de%20mon%20compte%20entra%C3%AEnera%20l%27annulation%20d%C3%A9finitive%20de%20l%27ensemble%20de%20mes%20r%C3%A9servations%20en%20cours.%0D%0A%0D%0AJ%27ai%2030%20jours%20pour%20me%20r%C3%A9tracter.%20Au-del%C3%A0%20de%20ce%20d%C3%A9lai%2C%20je%20ne%20pourrai%20plus%20acc%C3%A9der%20%C3%A0%20mon%20compte%20pass%20Culture%2C%20ni%20au%20cr%C3%A9dit%20%C3%A9ventuellement%20restant.%0D%0A%0D%0ABien%20cordialement%2C'

  return `mailto:${supportEmailAddress}?subject=${emailSubject}&body=${emailBody}`
}
