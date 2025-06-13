import {
  CollectiveOfferAllowedAction,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'

import { isActionAllowedOnCollectiveOffer } from './isActionAllowedOnCollectiveOffer'

function isOneOfActionAllowedOnCollectiveOffer(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel,
  actions: (CollectiveOfferAllowedAction | CollectiveOfferTemplateAllowedAction)[]
) {
  return actions.some(action =>
    isActionAllowedOnCollectiveOffer(offer, action)
  )
}

export function isCollectiveOfferSelectable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel,
) {
  return isOneOfActionAllowedOnCollectiveOffer(offer, [
    CollectiveOfferAllowedAction.CAN_ARCHIVE,
    CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
    CollectiveOfferTemplateAllowedAction.CAN_PUBLISH,
    CollectiveOfferTemplateAllowedAction.CAN_HIDE,
  ])
}