export const computeAllActivationSuccessMessage = (nbSelectedOffers: number) =>
  nbSelectedOffers > 1
    ? 'Les offres sont en cours d’activation, veuillez rafraichir dans quelques instants'
    : 'Une offre est en cours d’activation, veuillez rafraichir dans quelques instants'

export const computeAllDeactivationSuccessMessage = (
  nbSelectedOffers: number
) =>
  nbSelectedOffers > 1
    ? 'Les offres sont en cours de désactivation, veuillez rafraichir dans quelques instants'
    : 'Une offre est en cours de désactivation, veuillez rafraichir dans quelques instants'

export const computeActivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été publiées'
      : 'offre a bien été publiée'
  return `${nbSelectedOffers} ${successMessage}`
}

export const computeDeactivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été désactivées'
      : 'offre a bien été désactivée'
  return `${nbSelectedOffers} ${successMessage}`
}
