import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'core/OfferEducational/types'

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

//  Given any two offers in the offers tables, verify whether or not they are the same
export function isSameOffer(
  offer1: CollectiveOfferResponseModel | ListOffersOfferResponseModel,
  offer2: CollectiveOfferResponseModel | ListOffersOfferResponseModel
): boolean {
  if (isOfferEducational(offer1) !== isOfferEducational(offer2)) {
    return false
  }

  if (isOfferEducational(offer1)) {
    return offer1.isShowcase === offer2.isShowcase && offer1.id === offer2.id
  }
  return offer1.id === offer2.id
}
