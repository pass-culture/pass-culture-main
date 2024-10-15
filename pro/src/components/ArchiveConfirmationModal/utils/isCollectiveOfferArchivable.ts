import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  CollectiveOfferResponseModel,
} from 'apiClient/v1'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'commons/core/OfferEducational/types'

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
