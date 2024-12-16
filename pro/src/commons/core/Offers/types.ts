import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  OfferStatus,
} from 'apiClient/v1'
import { type EnumType } from 'commons/custom_types/utils'
import { CropParams } from 'components/ImageUploader/components/ButtonImageEdit/types'

import { ALL_FORMATS, ALL_STATUS } from './constants'

export type SearchFiltersParams = {
  nameOrIsbn: string
  offererId: string
  venueId: string
  categoryId: string
  format: EacFormat | typeof ALL_FORMATS
  status: OfferStatus | CollectiveOfferDisplayedStatus[] | typeof ALL_STATUS
  creationMode: string
  collectiveOfferType: string
  periodBeginningDate: string
  periodEndingDate: string
  offererAddressId: string
  page?: number
}

export type CollectiveSearchFiltersParams = {
  nameOrIsbn: string
  offererId: string
  venueId: string
  format: EacFormat | typeof ALL_FORMATS
  status: CollectiveOfferDisplayedStatus[]
  collectiveOfferType: CollectiveOfferTypeEnum
  periodBeginningDate: string
  periodEndingDate: string
  page?: number
}

export const CollectiveOfferTypeEnum = {
  ALL: 'all',
  OFFER: 'offer',
  TEMPLATE: 'template',
} as const
// eslint-disable-next-line no-redeclare
export type CollectiveOfferTypeEnum = EnumType<typeof CollectiveOfferTypeEnum>

export interface CategorySubtypeItem {
  code: number
  label: string
  children: {
    code: number
    label: string
  }[]
}

export interface OfferCollectiveImage {
  url?: string | null
  credit?: string | null
}

export interface IndividualOfferImage {
  originalUrl: string
  url: string
  credit: string | null
  cropParams?: CropParams
}
