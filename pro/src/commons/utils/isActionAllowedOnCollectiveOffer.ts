import {
  CollectiveOfferAllowedAction,
  type CollectiveOfferResponseModel as CollectiveOfferResponseModelOld,
  CollectiveOfferTemplateAllowedAction,
  type CollectiveOfferTemplateResponseModel as CollectiveOfferTemplateResponseModelOld,
  type GetCollectiveOfferResponseModel as GetCollectiveOfferResponseModelOld,
  type GetCollectiveOfferTemplateResponseModel as GetCollectiveOfferTemplateResponseModelOld,
} from '@/apiClient/v1'
import type {
  CollectiveOfferResponseModel as CollectiveOfferResponseModelNew,
  CollectiveOfferTemplateResponseModel as CollectiveOfferTemplateResponseModelNew,
  GetCollectiveOfferResponseModel as GetCollectiveOfferResponseModelNew,
  GetCollectiveOfferTemplateResponseModel as GetCollectiveOfferTemplateResponseModelNew,
} from '@/apiClient/v1/new'
import { isCollectiveOfferBookable } from '@/commons/core/OfferEducational/types'

type CollectiveOfferResponseModel =
  | CollectiveOfferResponseModelOld
  | CollectiveOfferResponseModelNew
type CollectiveOfferTemplateResponseModel =
  | CollectiveOfferTemplateResponseModelOld
  | CollectiveOfferTemplateResponseModelNew
type GetCollectiveOfferResponseModel =
  | GetCollectiveOfferResponseModelOld
  | GetCollectiveOfferResponseModelNew
type GetCollectiveOfferTemplateResponseModel =
  | GetCollectiveOfferTemplateResponseModelOld
  | GetCollectiveOfferTemplateResponseModelNew

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
