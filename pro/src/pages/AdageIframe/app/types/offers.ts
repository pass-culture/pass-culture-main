import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { hasProperty } from 'utils/types'

export type EducationalDomain = {
  id: number
  name: string
}

export type HydratedCollectiveOffer = CollectiveOfferResponseModel & {
  isTemplate: false
}

export const isCollectiveOffer = (
  value: unknown
): value is HydratedCollectiveOffer =>
  hasProperty(value, 'isTemplate') && value.isTemplate === false

export type HydratedCollectiveOfferTemplate =
  CollectiveOfferTemplateResponseModel & { isTemplate: true }
