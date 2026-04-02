import type {
  CollectiveOfferHomeResponseModel,
  CollectiveOfferTemplateHomeResponseModel,
} from '@/apiClient/v1'

export enum HomepageVariant {
  COLLECTIVE = 'collective',
  INDIVIDUAL = 'individual',
}

export interface CollectiveOffersVariantMap {
  BOOKABLE: CollectiveOfferHomeResponseModel
  TEMPLATE: CollectiveOfferTemplateHomeResponseModel
}

export type CollectiveOffersCardVariant = keyof CollectiveOffersVariantMap

export type OffersCardVariant = CollectiveOffersCardVariant | 'INDIVIDUAL'
