export const computeDeletionSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'Les brouillons ont bien été supprimés'
      : 'Le brouillon a bien été supprimé'
  return successMessage
}
