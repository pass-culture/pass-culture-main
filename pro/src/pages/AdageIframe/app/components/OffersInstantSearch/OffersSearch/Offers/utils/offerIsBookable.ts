import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adageIframe'

export const offerIsBookable = (
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
): boolean => !offer.isSoldOut && !offer.isExpired
