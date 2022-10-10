export const computeDeletionSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'brouillons ont bien été supprimés'
      : 'brouillon a bien été supprimé'
  return `${nbSelectedOffers} ${successMessage}`
}
