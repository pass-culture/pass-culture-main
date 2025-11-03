import {
  CollectiveOfferAllowedAction,
  type CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  type CollectiveOfferTemplateResponseModel,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { isCollectiveOfferBookable } from '@/commons/core/OfferEducational/types'

export function isActionAllowedOnCollectiveOffer(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel
    | CollectiveOfferTemplateResponseModel,
  action: CollectiveOfferAllowedAction | CollectiveOfferTemplateAllowedAction
) {
  if (isCollectiveOfferBookable(offer)) {
    return (offer.allowedActions as CollectiveOfferAllowedAction[]).includes(
      action as CollectiveOfferAllowedAction
    )
  }
  return (
    offer.allowedActions as CollectiveOfferTemplateAllowedAction[]
  ).includes(action as CollectiveOfferTemplateAllowedAction)
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
    | CollectiveOfferResponseModel
    | CollectiveOfferTemplateResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
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
    | CollectiveOfferTemplateResponseModel
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
