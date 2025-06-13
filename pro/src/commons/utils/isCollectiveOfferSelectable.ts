import {
  CollectiveOfferAllowedAction,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'



export function isCollectiveOfferSelectable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel,
) {
  return offer.allowedActions.some((action) => [
    CollectiveOfferAllowedAction.CAN_ARCHIVE,
    CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
    CollectiveOfferTemplateAllowedAction.CAN_PUBLISH,
    CollectiveOfferTemplateAllowedAction.CAN_HIDE,
  ].includes(action))
}