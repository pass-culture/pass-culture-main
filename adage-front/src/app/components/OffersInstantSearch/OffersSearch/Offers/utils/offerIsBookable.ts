import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient'

export const offerIsBookable = (
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
): boolean => !offer.isSoldOut && !offer.isExpired
