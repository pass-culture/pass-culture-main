import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient//adage'

export const offerIsBookable = (
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
): boolean => !offer.isSoldOut && !offer.isExpired
