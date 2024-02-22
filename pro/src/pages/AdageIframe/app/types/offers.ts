import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'

export const isCollectiveOfferTemplate = (
  value: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
): value is CollectiveOfferTemplateResponseModel => Boolean(value.isTemplate)

export const isCollectiveOfferBookable = (
  value: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
): value is CollectiveOfferResponseModel => !value.isTemplate
