// This file will be replace by apiClient
/* istanbul ignore file */

import { DEFAULT_INVOICES_FILTERS } from 'components/pages/Reimbursements/_constants'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings'
import { ReimbursementPointsResponseModel } from 'core/Finances'
import { EducationalDomain } from 'core/OfferEducational'
import { client } from 'repository/pcapi/pcapiClient'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'
import { stringify } from 'utils/query-string'

//
// venues
//

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venue' implicitly has an 'any' type.
export const createVenue = venue => client.post(`/venues`, venue)

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueId' implicitly has an 'any' type.
export const editVenue = (venueId, body) =>
  client.patch(`/venues/${venueId}`, body)

export const postImageToVenue = async ({
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'venueId' implicitly has an 'any' ... Remove this comment to see the full error message
  venueId,
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'banner' implicitly has an 'any' t... Remove this comment to see the full error message
  banner,
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'xCropPercent' implicitly has an '... Remove this comment to see the full error message
  xCropPercent,
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'yCropPercent' implicitly has an '... Remove this comment to see the full error message
  yCropPercent,
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'heightCropPercent' implicitly has... Remove this comment to see the full error message
  heightCropPercent,
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'widthCropPercent' implicitly has... Remove this comment to see the full error message
  widthCropPercent,
  // @ts-expect-error ts-migrate(7031) FIXME: Binding element 'imageCredit' implicitly has an 'a... Remove this comment to see the full error message
  imageCredit,
}) => {
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

  const queryParams = stringify(venueImage)

  return await client.postWithFormData(
    `/venues/${venueId}/banner?${queryParams}`,
    body
  )
}

//
// thumbnail
//

export const postThumbnail = (
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offerId' implicitly has an 'any' type.
  offerId,
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'credit' implicitly has an 'any' type.
  credit,
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'thumb' implicitly has an 'any' type.
  thumb,
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'thumbUrl' implicitly has an 'any' type.
  thumbUrl,
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'x' implicitly has an 'any' type.
  x,
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'y' implicitly has an 'any' type.
  y,
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'height' implicitly has an 'any' type.
  height,
  // @ts-expect-error ts-migrate(7006) FIXME: Parameter 'width' implicitly has an 'any' type.
  width
) => {
  const body = new FormData()
  body.append('offerId', offerId)
  body.append('credit', credit)
  body.append('croppingRectX', x)
  body.append('croppingRectY', y)
  body.append('croppingRectHeight', height)
  body.append('croppingRectWidth', width)
  body.append('thumb', thumb)
  body.append('thumbUrl', thumbUrl)

  return client.postWithFormData('/offers/thumbnails', body)
}

//
// Providers
//

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueId' implicitly has an 'any' type.
export const loadProviders = async venueId => {
  return client.get(`/providers/${venueId}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueId' implicitly has an 'any' type.
export const loadVenueProviders = async venueId => {
  return client
    .get(`/venueProviders?venueId=${venueId}`)
    .then(response => response.venue_providers)
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
    params.eventDate = formatBrowserTimezonedDateAsUTC(
      eventDate,
      FORMAT_ISO_DATE_ONLY
    )
  }
  if (bookingPeriodBeginningDate) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'bookingPeriodBeginningDate' does not exi... Remove this comment to see the full error message
    params.bookingPeriodBeginningDate = formatBrowserTimezonedDateAsUTC(
      bookingPeriodBeginningDate,
      FORMAT_ISO_DATE_ONLY
    )
  }

  if (bookingPeriodEndingDate) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'bookingPeriodEndingDate' does not exist ... Remove this comment to see the full error message
    params.bookingPeriodEndingDate = formatBrowserTimezonedDateAsUTC(
      bookingPeriodEndingDate,
      FORMAT_ISO_DATE_ONLY
    )
  }

  // @ts-expect-error ts-migrate(2339) FIXME: Property 'bookingStatusFilter' does not exist on t... Remove this comment to see the full error message
  params.bookingStatusFilter = bookingStatusFilter

  return stringify(params)
}

export const getUserHasBookings = async () => {
  return client.get(`/bookings/pro/userHasBookings`)
}

export const getUserHasCollectiveBookings = async () => {
  return client.get(`/collective/bookings/pro/userHasBookings`)
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

//
// Booking
//

//
// Business Unit
//

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offererId' implicitly has an 'any' type... Remove this comment to see the full error message
export const getBusinessUnits = offererId => {
  const queryParams = offererId ? `?offererId=${offererId}` : ''

  return client.get(`/finance/business-units${queryParams}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'businessUnitId' implicitly has an 'any'... Remove this comment to see the full error message
export const editBusinessUnit = (businessUnitId, siret) => {
  return client.patch(`/finance/business-units/${businessUnitId}`, {
    siret: siret,
  })
}

//
// Reimbursement Point
//
export const getReimbursementPoints = (
  offererId = null
): Promise<ReimbursementPointsResponseModel[]> => {
  const queryParams = offererId ? `?offererId=${offererId}` : ''

  return client.get(`/finance/reimbursement-points${queryParams}`)
}

//
// Invoices
//

const buildInvoicesQuery = ({
  businessUnitId = DEFAULT_INVOICES_FILTERS.businessUnitId,
  reimbursementPointId = DEFAULT_INVOICES_FILTERS.businessUnitId,
  periodBeginningDate = DEFAULT_INVOICES_FILTERS.periodBeginningDate,
  periodEndingDate = DEFAULT_INVOICES_FILTERS.periodEndingDate,
}) => {
  const params = {}
  if (businessUnitId !== DEFAULT_INVOICES_FILTERS.businessUnitId) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'businessUnitId' does not exist on type '... Remove this comment to see the full error message
    params.businessUnitId = businessUnitId
  }

  if (reimbursementPointId !== DEFAULT_INVOICES_FILTERS.businessUnitId) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'reimbursementPointId' does not exist on type '... Remove this comment to see the full error message
    params.reimbursementPointId = reimbursementPointId
  }

  if (periodBeginningDate !== DEFAULT_INVOICES_FILTERS.periodBeginningDate) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'periodBeginningDate' does not exist on t... Remove this comment to see the full error message
    params.periodBeginningDate = formatBrowserTimezonedDateAsUTC(
      periodBeginningDate,
      FORMAT_ISO_DATE_ONLY
    )
  }

  if (periodEndingDate !== DEFAULT_INVOICES_FILTERS.periodEndingDate) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'periodEndingDate' does not exist on type... Remove this comment to see the full error message
    params.periodEndingDate = formatBrowserTimezonedDateAsUTC(
      periodEndingDate,
      FORMAT_ISO_DATE_ONLY
    )
  }

  return stringify(params)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'params' implicitly has an 'any' type.
export const getInvoices = async params => {
  const queryParams = buildInvoicesQuery(params)
  return client.get(`/finance/invoices?${queryParams}`)
}

// Domains
export const getEducationalDomains = async (): Promise<EducationalDomain[]> =>
  client.get('/collective/educational-domains')
