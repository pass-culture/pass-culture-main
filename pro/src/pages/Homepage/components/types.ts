import type {
  CollectiveOfferHomeResponseModel,
  CollectiveOfferTemplateHomeResponseModel,
} from '@/apiClient/v1/new'

export enum HomepageVariant {
  COLLECTIVE = 'collective',
  INDIVIDUAL = 'individual',
}

export interface CollectiveOffersVariantMap {
  BOOKABLE: CollectiveOfferHomeResponseModel
  TEMPLATE: CollectiveOfferTemplateHomeResponseModel
}

export type CollectiveOffersCardVariant = keyof CollectiveOffersVariantMap

export const OffersCardVariant = {
  BOOKABLE: 'BOOKABLE',
  TEMPLATE: 'TEMPLATE',
  INDIVIDUAL: 'INDIVIDUAL',
} as const satisfies Record<CollectiveOffersCardVariant | 'INDIVIDUAL', string>

export type OffersCardVariant = keyof typeof OffersCardVariant
