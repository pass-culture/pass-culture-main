export const computeDeletionSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? `${nbSelectedOffers} brouillons ont bien été supprimés`
      : `${nbSelectedOffers} brouillon a bien été supprimé`
  return successMessage
}
