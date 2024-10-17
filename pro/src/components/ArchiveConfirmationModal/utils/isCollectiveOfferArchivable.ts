import {
  CollectiveOfferAllowedAction,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational/types'

export function isCollectiveOfferArchivable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel
) {
  const canArchiveThisOffer =
    (isCollectiveOffer(offer) &&
      offer.allowedActions.includes(
        CollectiveOfferAllowedAction.CAN_ARCHIVE
      )) ||
    (isCollectiveOfferTemplate(offer) &&
      offer.allowedActions.includes(
        CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
      ))

  return canArchiveThisOffer
}
