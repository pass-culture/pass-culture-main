export const computeDeletionSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'brouillons ont bien été supprimés'
      : 'brouillon a bien été supprimé'
  return `${nbSelectedOffers} ${successMessage}`
}

export const computeDeletionErrorMessage = (nbSelectedOffers: number) => {
  return nbSelectedOffers > 1
    ? `Une erreur est survenue lors de la suppression des brouillon`
    : `Une erreur est survenue lors de la suppression du brouillon`
}
