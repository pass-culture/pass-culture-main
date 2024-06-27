import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isOfferEducational } from 'core/OfferEducational/types'

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
