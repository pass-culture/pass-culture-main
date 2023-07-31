// This file will be replace by apiClient
/* istanbul ignore file */

import {
  AttachImageResponseModel,
  CreateThumbnailResponseModel,
} from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { client } from 'repository/pcapi/pcapiClient'
import { stringify } from 'utils/query-string'

//
// venues
//

export const postImageToVenue = async (
  venueId: number,
  banner: File,
  imageCredit: string | null,
  xCropPercent?: number,
  yCropPercent?: number,
  heightCropPercent?: number,
  widthCropPercent?: number
) => {
  const body = new FormData()
  body.append('banner', banner)

  const venueImage = {
    x_crop_percent: xCropPercent,
    y_crop_percent: yCropPercent,
    height_crop_percent: heightCropPercent,
    width_crop_percent: widthCropPercent,
  }

  if (imageCredit) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'image_credit' does not exist on type '{ ... Remove this comment to see the full error message
    venueImage.image_credit = imageCredit
  }

  // @ts-expect-error
  const queryParams = stringify(venueImage)

  return await client.postWithFormData(
    `/venues/${venueId}/banner?${queryParams}`,
    body
  )
}

//
// thumbnail
//

type LegacyPostImageMethodType<T> = (
  offerId: string,
  thumb: File,
  credit: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => Promise<T>

export const legacyPostImage = (
  url: string,
  offerId: string,
  thumb: File,
  credit?: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => {
  const body = new FormData()
  body.append('offerId', offerId)
  body.append('thumb', thumb)
  body.append('credit', credit ?? '')
  body.append('croppingRectX', x !== undefined ? String(x) : '')
  body.append('croppingRectY', y !== undefined ? String(y) : '')
  body.append('croppingRectHeight', height !== undefined ? String(height) : '')
  body.append('croppingRectWidth', width !== undefined ? String(width) : '')
  body.append('thumbUrl', thumbUrl ?? '')

  return client.postWithFormData(url, body)
}

type PostImageMethodType<T> = (
  offerId: number,
  thumb: File,
  credit: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => Promise<T>

export const postImage = (
  url: string,
  offerId: number,
  thumb: File,
  credit?: string | null,
  thumbUrl?: string,
  x?: number,
  y?: number,
  height?: number,
  width?: number
) => {
  const body = new FormData()
  body.append('offerId', offerId.toString())
  body.append('thumb', thumb)
  body.append('credit', credit ?? '')
  body.append('croppingRectX', x !== undefined ? String(x) : '')
  body.append('croppingRectY', y !== undefined ? String(y) : '')
  body.append('croppingRectHeight', height !== undefined ? String(height) : '')
  body.append('croppingRectWidth', width !== undefined ? String(width) : '')
  body.append('thumbUrl', thumbUrl ?? '')

  return client.postWithFormData(url, body)
}

export const postThumbnail: LegacyPostImageMethodType<
  CreateThumbnailResponseModel
> = (...args) => legacyPostImage('/offers/thumbnails', ...args)

export const postCollectiveOfferImage: PostImageMethodType<
  AttachImageResponseModel
> = (offerId, ...args) =>
  postImage(`/collective/offers/${offerId}/image`, offerId, ...args)

export const postCollectiveOfferTemplateImage: PostImageMethodType<
  AttachImageResponseModel
> = (offerId, ...args) =>
  postImage(`/collective/offers-template/${offerId}/image`, offerId, ...args)

//
// Providers
//

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueId' implicitly has an 'any' type.
export const loadProviders = async venueId => {
  return client.get(`/providers/${venueId}`)
}

//
// BookingsRecap
//
export const buildBookingsRecapQuery = ({
  venueId = DEFAULT_PRE_FILTERS.offerVenueId,
  eventDate = DEFAULT_PRE_FILTERS.offerEventDate,
  bookingPeriodBeginningDate = DEFAULT_PRE_FILTERS.bookingBeginningDate,
  bookingPeriodEndingDate = DEFAULT_PRE_FILTERS.bookingEndingDate,
  bookingStatusFilter = DEFAULT_PRE_FILTERS.bookingStatusFilter,
  offerType = DEFAULT_PRE_FILTERS.offerType,
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'page' implicitly has an 'any' typ... Remove this comment to see the full error message
  page,
}) => {
  const params = { page }

  if (venueId !== DEFAULT_PRE_FILTERS.offerVenueId) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'venueId' does not exist on type '{ page:... Remove this comment to see the full error message
    params.venueId = venueId
  }
  if (offerType !== DEFAULT_PRE_FILTERS.offerType) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'offerType' does not exist on type '{ pag... Remove this comment to see the full error message
    params.offerType = offerType
  }
  if (eventDate !== DEFAULT_PRE_FILTERS.offerEventDate) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'eventDate' does not exist on type '{ pag... Remove this comment to see the full error message
    params.eventDate = eventDate
  }
  if (bookingPeriodBeginningDate) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'bookingPeriodBeginningDate' does not exi... Remove this comment to see the full error message
    params.bookingPeriodBeginningDate = bookingPeriodBeginningDate
  }

  if (bookingPeriodEndingDate) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'bookingPeriodEndingDate' does not exist ... Remove this comment to see the full error message
    params.bookingPeriodEndingDate = bookingPeriodEndingDate
  }

  // @ts-expect-error ts-migrate(2339) FIXME: Property 'bookingStatusFilter' does not exist on t... Remove this comment to see the full error message
  params.bookingStatusFilter = bookingStatusFilter

  return stringify(params)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'filters' implicitly has an 'any' type.
export const getFilteredBookingsCSV = async filters => {
  const queryParams = buildBookingsRecapQuery(filters)
  return client.getPlainText(`/bookings/csv?${queryParams}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'filters' implicitly has an 'any' type.
export const getFilteredBookingsXLS = async filters => {
  const queryParams = buildBookingsRecapQuery(filters)
  return client.getExcelFile(`/bookings/excel?${queryParams}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'filters' implicitly has an 'any' type.
export const getFilteredCollectiveBookingsCSV = async filters => {
  const queryParams = buildBookingsRecapQuery(filters)
  return client.getPlainText(`/collective/bookings/csv?${queryParams}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'filters' implicitly has an 'any' type.
export const getFilteredCollectiveBookingsXLS = async filters => {
  const queryParams = buildBookingsRecapQuery(filters)
  return client.getExcelFile(`/collective/bookings/excel?${queryParams}`)
}
