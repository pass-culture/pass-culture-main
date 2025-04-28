import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  OfferStatus,
} from 'apiClient/v1'
import { CropParams } from 'commons/utils/imageUploadTypes'

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

export enum CollectiveOfferTypeEnum {
  ALL = 'all',
  OFFER = 'offer',
  TEMPLATE = 'template',
}

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
