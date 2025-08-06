import {
  CollectiveOfferAllowedAction,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from '@/commons/core/OfferEducational/types'

export function isCollectiveOfferArchivable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel
) {
  return (
    (isCollectiveOffer(offer) &&
      offer.allowedActions.includes(
        CollectiveOfferAllowedAction.CAN_ARCHIVE
      )) ||
    (isCollectiveOfferTemplate(offer) &&
      offer.allowedActions.includes(
        CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
      ))
  )
}
