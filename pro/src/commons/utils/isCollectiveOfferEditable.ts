import {
  CollectiveOfferAllowedAction,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'


export function isCollectiveOfferEditable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel,
) {
  return offer.allowedActions.some((action) => [
    CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
    CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
  ].includes(action))
}