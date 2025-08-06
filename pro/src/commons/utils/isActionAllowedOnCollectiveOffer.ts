import {
  CollectiveOfferAllowedAction,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient//v1'
import {
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from '@/commons/core/OfferEducational/types'

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

export function isCollectiveOfferDetailsEditable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel
) {
  return offer.allowedActions.some((action) =>
    [
      CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
      CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
    ].includes(action)
  )
}

export function isCollectiveOfferSelectable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel
) {
  return offer.allowedActions.some((action) =>
    [
      CollectiveOfferAllowedAction.CAN_ARCHIVE,
      CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
      CollectiveOfferTemplateAllowedAction.CAN_PUBLISH,
      CollectiveOfferTemplateAllowedAction.CAN_HIDE,
    ].includes(action)
  )
}

export function isCollectiveStockEditable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
) {
  return offer.allowedActions.some((action) =>
    [
      CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
    ].includes(action as CollectiveOfferAllowedAction)
  )
}

export function isCollectiveOfferEditable(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel
) {
  return offer.allowedActions.some((action) =>
    [
      CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
      CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
      CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
      CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
    ].includes(action)
  )
}
