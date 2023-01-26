import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adageIframe'

export type EducationalDomain = {
  id: number
  name: string
}

export type HydratedCollectiveOffer = CollectiveOfferResponseModel & {
  isTemplate: false
}
export type HydratedCollectiveOfferTemplate =
  CollectiveOfferTemplateResponseModel & { isTemplate: true }
