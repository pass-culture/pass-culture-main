export const computeDeletionErrorMessage = (nbSelectedOffers: number) => {
  return nbSelectedOffers > 1
    ? `Une erreur est survenue lors de la suppression des brouillon`
    : `Une erreur est survenue lors de la suppression du brouillon`
}
