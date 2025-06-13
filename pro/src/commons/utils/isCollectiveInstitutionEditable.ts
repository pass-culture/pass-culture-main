import {
  CollectiveOfferAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'


export function isCollectiveInstitutionEditable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
) {
  const allowedActions = offer.allowedActions as CollectiveOfferAllowedAction[]

  return allowedActions.includes(
    CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION
  )
}
