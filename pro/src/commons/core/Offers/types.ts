import type { EacFormat } from '@/apiClient/adage'
import type { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import type { CropParams } from '@/commons/utils/imageUploadTypes'

import type { ALL_FORMATS } from './constants'

export type Pagination = {
  page?: number
}

// TODO (tpommellet) check if it is still necessary once GetIndividualOfferWithAddressResponseModel is migrated to Pydantic V2
/**
 * Type of an individual offer's `extraData`, which the API exposes as an untyped object.
 */
export type OfferExtraData = {
  author?: string
  ean?: string
  gtl_id?: string
  performer?: string
  showSubType?: string
  showType?: string
  speaker?: string
  stageDirector?: string
  visa?: string
}

export type CollectiveSearchFiltersParams = Pagination & {
  name: string
  // TODO (igabriele, 2025-11-07): Should be a number. "all" is a case that never happens since there is always a `currentOfferer` in the store.
  offererId?: string | 'all'
  // TODO (igabriele, 2025-11-07): Should be a number. "all" is a case that will disappear once `WIP_SWITCH_VENUE` is enabled in production.
  venueId: string | 'all'
  status: CollectiveOfferDisplayedStatus[]
  periodBeginningDate: string
  periodEndingDate: string
  locationType?: string
  offererAddressId?: string
  format: EacFormat | typeof ALL_FORMATS
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
