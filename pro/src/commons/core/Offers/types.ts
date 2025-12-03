import type { EacFormat } from '@/apiClient/adage'
import type {
  CollectiveOfferDisplayedStatus,
  OfferStatus,
} from '@/apiClient/v1'
import type { CropParams } from '@/commons/utils/imageUploadTypes'

import type { ALL_FORMATS, ALL_STATUS } from './constants'

type SearchListParams = {
  format: EacFormat | typeof ALL_FORMATS
  page?: number
}

export type IndividualSearchFiltersParams = SearchListParams & {
  nameOrIsbn: string
  // TODO (igabriele, 2025-11-07): Should be a number. "all" is a case that never happens since there is always a `currentOfferer` in the store.
  offererId: string
  // TODO (igabriele, 2025-11-07): Should be a number. "all" is a case that will disappear once `WIP_SWITCH_VENUE` is enabled in production.
  venueId: string
  categoryId: string
  status: OfferStatus | typeof ALL_STATUS
  creationMode: string
  periodBeginningDate: string
  periodEndingDate: string
  offererAddressId: string
}

export type CollectiveSearchFiltersParams = SearchListParams & {
  name: string
  // TODO (igabriele, 2025-11-07): Should be a number. "all" is a case that never happens since there is always a `currentOfferer` in the store.
  offererId: string | 'all'
  // TODO (igabriele, 2025-11-07): Should be a number. "all" is a case that will disappear once `WIP_SWITCH_VENUE` is enabled in production.
  venueId: string | 'all'
  status: CollectiveOfferDisplayedStatus[]
  collectiveOfferType: CollectiveOfferTypeEnum
  periodBeginningDate: string
  periodEndingDate: string
  locationType?: string
  offererAddressId?: string
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
  url?: string
  credit: string | null
  cropParams?: CropParams
}
