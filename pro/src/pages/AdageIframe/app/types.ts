import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'

export type Facets = (string | string[])[]

export type Option<T = string> = { value: T; label: string }

export const isCollectiveOfferTemplate = (
  value: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
): value is CollectiveOfferTemplateResponseModel => Boolean(value.isTemplate)

export const isCollectiveOfferBookable = (
  value: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
): value is CollectiveOfferResponseModel => !value.isTemplate
