export const computeDeletionSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'Les brouillons ont bien été supprimés'
      : 'Le brouillon a bien été supprimé'
  return successMessage
}

export const computeDeletionErrorMessage = (nbSelectedOffers: number) => {
  return nbSelectedOffers > 1
    ? `Une erreur est survenue lors de la suppression des brouillon`
    : `Une erreur est survenue lors de la suppression du brouillon`
}
