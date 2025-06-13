import {
  CollectiveOfferAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'


export function isCollectiveStockEditable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
) {
  return offer.allowedActions.some((action) => [
    CollectiveOfferAllowedAction.CAN_EDIT_DATES,
    CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
  ].includes(action as CollectiveOfferAllowedAction))
}
