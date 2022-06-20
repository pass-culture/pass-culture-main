import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'api/gen'

// only collective offer has "stock" entry in response payload
export const isOfferCollectiveOffer = (
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
): offer is CollectiveOfferResponseModel => 'stock' in offer
