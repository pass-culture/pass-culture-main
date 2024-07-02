import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  OfferStatus,
} from 'apiClient/v1'
import { CropParams } from 'components/ImageUploader/ButtonImageEdit/types'

import { ALL_FORMATS, ALL_STATUS } from './constants'

export type SearchFiltersParams = {
  nameOrIsbn: string
  offererId: string
  venueId: string
  categoryId: string
  format: EacFormat | typeof ALL_FORMATS
  status: OfferStatus | CollectiveOfferDisplayedStatus | typeof ALL_STATUS
  creationMode: string
  collectiveOfferType: string
  periodBeginningDate: string
  periodEndingDate: string
  offererAddressId: string
  page?: number
  offererAddressId: string
}

export interface CategorySubtypeItem {
  code: number
  label: string
  children: {
    code: number
    label: string
  }[]
}

// TODO: this should be generated in openapi schema
export interface OfferExtraData {
  author?: string
  gtl_id?: string
  musicType?: string
  musicSubType?: string
  performer?: string
  ean?: string
  showType?: string
  showSubType?: string
  speaker?: string
  stageDirector?: string
  visa?: string
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
