export const computeActivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été publiées'
      : 'offre a bien été publiée'
  return `${nbSelectedOffers} ${successMessage}`
}
