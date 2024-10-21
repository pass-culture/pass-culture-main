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
} from 'commons/core/OfferEducational/types'

export function isActionAllowedOnCollectiveOffer(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel,
  action: CollectiveOfferAllowedAction | CollectiveOfferTemplateAllowedAction
) {
  if (isCollectiveOffer(offer)) {
    return offer.allowedActions.includes(action as CollectiveOfferAllowedAction)
  }

  if (isCollectiveOfferTemplate(offer)) {
    return offer.allowedActions.includes(
      action as CollectiveOfferTemplateAllowedAction
    )
  }

  return false
}
