import type {
  CollectiveOfferHomeResponseModel,
  CollectiveOfferTemplateHomeResponseModel,
} from '@/apiClient/v1'

export enum HomepageVariant {
  COLLECTIVE = 'collective',
  INDIVIDUAL = 'individual',
}

export enum OffersCardVariant {
  TEMPLATE = 'template',
  BOOKABLE = 'bookable',
  INDIVIDUAL = 'individual',
}

export enum CollectiveOffersCardVariant {
  TEMPLATE = 'template',
  BOOKABLE = 'bookable',
}

export interface CollectiveOffersVariantMap {
  [CollectiveOffersCardVariant.BOOKABLE]: CollectiveOfferHomeResponseModel
  [CollectiveOffersCardVariant.TEMPLATE]: CollectiveOfferTemplateHomeResponseModel
}
