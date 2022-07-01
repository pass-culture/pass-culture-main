import { ALL_OFFERERS, DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import {
  FORMAT_ISO_DATE_ONLY,
  formatBrowserTimezonedDateAsUTC,
} from 'utils/date'

import { DEFAULT_INVOICES_FILTERS } from 'components/pages/Reimbursements/_constants'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings'
import { EducationalDomain } from 'core/OfferEducational'
import { ListOffersQueryModel } from 'apiClient/v1'
import { client } from 'repository/pcapi/pcapiClient'
import { stringify } from 'utils/query-string'

export const loadFeatures = async () => {
  client.get('/features')
  return client.get('/features')
}

//
// offers
//
// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offerId' implicitly has an 'any' type.
export const loadOffer = async offerId => {
  return client.get(`/offers/${offerId}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offer' implicitly has an 'any' type.
export const createOffer = offer => {
  return client.post(`/offers`, offer)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offerId' implicitly has an 'any' type.
export const updateOffer = (offerId, offer) => {
  return client.patch(`/offers/${offerId}`, offer)
}

export const publishOffer = (offerId: string) => {
  return client.patch(`/offers/publish`, { id: offerId })
}

export const patchIsCollectiveOfferActive = (
  offerIds: string[],
  isActive: boolean
) => {
  return client.patch(`/collective/offers/active-status`, {
    ids: offerIds,
    isActive,
  })
}

export const loadFilteredOffers = async ({
  nameOrIsbn = DEFAULT_SEARCH_FILTERS.nameOrIsbn,
  offererId = DEFAULT_SEARCH_FILTERS.offererId,
  venueId = DEFAULT_SEARCH_FILTERS.venueId,
  categoryId = DEFAULT_SEARCH_FILTERS.categoryId,
  periodBeginningDate = DEFAULT_SEARCH_FILTERS.periodBeginningDate,
  periodEndingDate = DEFAULT_SEARCH_FILTERS.periodEndingDate,
  status = DEFAULT_SEARCH_FILTERS.status,
  creationMode = DEFAULT_SEARCH_FILTERS.creationMode,
}) => {
  const body = createRequestBody({
    nameOrIsbn,
    offererId,
    venueId,
    categoryId,
    status,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
  })

  const queryParams = stringify(body)
  return client.get(`/offers${queryParams ? `?${queryParams}` : ''}`)
}

export const updateOffersActiveStatus = (ids: string[], isActive: boolean) =>
  client.patch('/offers/active-status', { ids, isActive })

export const updateAllOffersActiveStatus = (
  body: ListOffersQueryModel & { isActive: boolean }
) => client.patch('/offers/all-active-status', body)

export const updateAllCollectiveOffersActiveStatus = (
  body: ListOffersQueryModel & { isActive: boolean }
) => client.patch('/collective/offers/all-active-status', body)

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'searchFilters' implicitly has an 'any' ... Remove this comment to see the full error message
const createRequestBody = searchFilters => {
  const body = {}
  Object.keys(DEFAULT_SEARCH_FILTERS).forEach(field => {
    if (
      searchFilters[field] &&
      // @ts-expect-error ts-migrate(7053) FIXME: Element implicitly has an 'any' type because expre... Remove this comment to see the full error message
      searchFilters[field] !== DEFAULT_SEARCH_FILTERS[field]
    ) {
      // @ts-expect-error ts-migrate(7053) FIXME: Element implicitly has an 'any' type because expre... Remove this comment to see the full error message
      body[field] = searchFilters[field]
    }
  })

  if (searchFilters.page) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'page' does not exist on type '{}'.
    body.page = searchFilters.page
  }

  if (
    searchFilters.periodBeginningDate !==
    DEFAULT_SEARCH_FILTERS.periodBeginningDate
  ) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'periodBeginningDate' does not exist on t... Remove this comment to see the full error message
    body.periodBeginningDate = searchFilters.periodBeginningDate
  }

  if (
    searchFilters.periodEndingDate !== DEFAULT_SEARCH_FILTERS.periodEndingDate
  ) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'periodEndingDate' does not exist on type... Remove this comment to see the full error message
    body.periodEndingDate = searchFilters.periodEndingDate
  }

  return body
}

//
// offerers
//

export const getAllOfferersNames = () => {
  return client.get('/offerers/names').then(response => response.offerersNames)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offererId' implicitly has an 'any' type... Remove this comment to see the full error message
export const generateOffererApiKey = async offererId => {
  return client
    .post(`/offerers/${offererId}/api_keys`, {})
    .then(response => response.apiKey)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'apiKey' implicitly has an 'any' type.
export const deleteOffererApiKey = async apiKey => {
  return client.delete(`/offerers/api_keys/${apiKey}`)
}

export const getUserValidatedOfferersNames = () => {
  return client
    .get('/offerers/names?validated_for_user=true')
    .then(response => response.offerersNames)
}

export const buildGetOfferersQuery = ({ keywords = [], page = 1 }) => {
  const apiQueryParams = {}
  if (keywords.length > 0) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'keywords' does not exist on type '{}'.
    apiQueryParams.keywords = keywords.join(' ')
  }

  // @ts-expect-error ts-migrate(2339) FIXME: Property 'page' does not exist on type '{}'.
  apiQueryParams.page = page

  return `?${stringify(apiQueryParams)}`
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'filters' implicitly has an 'any' type.
export const getOfferers = filters => {
  const queryParams = buildGetOfferersQuery(filters)
  return client.get(`/offerers${queryParams}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offererId' implicitly has an 'any' type... Remove this comment to see the full error message
export const getOfferer = offererId => {
  return client.get(`/offerers/${offererId}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offererId' implicitly has an 'any' type... Remove this comment to see the full error message
export const canOffererCreateEducationalOffer = offererId =>
  client.get(`/offerers/${offererId}/eac-eligibility`)

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offererId' implicitly has an 'any' type... Remove this comment to see the full error message
export const getEducationalOfferers = offererId => {
  const queryParams = `${offererId ? `?offerer_id=${offererId}` : ''}`
  return client.get(`/offerers/educational${queryParams}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offerer' implicitly has an 'any' type.
export const createOfferer = offerer => client.post(`/offerers`, offerer)

//
// venues
//
export const getVenuesForOfferer = ({
  offererId = null,
  activeOfferersOnly = false,
} = {}) => {
  const request = {}
  if (offererId) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'offererId' does not exist on type '{}'.
    if (offererId !== ALL_OFFERERS) request.offererId = offererId
  } else {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'validatedForUser' does not exist on type... Remove this comment to see the full error message
    request.validatedForUser = true
  }

  // @ts-expect-error ts-migrate(2339) FIXME: Property 'activeOfferersOnly' does not exist on ty... Remove this comment to see the full error message
  if (activeOfferersOnly) request.activeOfferersOnly = true
  const queryParams = stringify(request)
  const url = queryParams !== '' ? `/venues?${queryParams}` : '/venues'
  return client.get(url).then(response => response.venues)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueId' implicitly has an 'any' type.
export const getVenue = venueId => client.get(`/venues/${venueId}`)

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venue' implicitly has an 'any' type.
export const createVenue = venue => client.post(`/venues`, venue)

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueId' implicitly has an 'any' type.
export const editVenue = (venueId, body) =>
  client.patch(`/venues/${venueId}`, body)

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueId' implicitly has an 'any' type.
export const getVenueStats = venueId => client.get(`/venues/${venueId}/stats`)

export const getVenueTypes = () => client.get(`/venue-types`)

export const getVenueLabels = () => client.get(`/venue-labels`)

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

// @ts-expect-error ts-migrate(7031) FIXME: Binding element 'venueId' implicitly has an 'any' ... Remove this comment to see the full error message
export const deleteVenueImage = async ({ venueId }) => {
  return await client.delete(`/venues/${venueId}/banner`)
}

//
// types
//
export const loadTypes = () => {
  return client.get('/types')
}

//
// categories
//
export const loadCategories = () => {
  return client.get('/offers/categories')
}

//
// stocks
//
// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offerId' implicitly has an 'any' type.
export const loadStocks = offerId => {
  return client.get(`/offers/${offerId}/stocks`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offerId' implicitly has an 'any' type.
export const bulkCreateOrEditStock = (offerId, stocks) => {
  return client.post(`/stocks/bulk`, {
    offerId,
    stocks,
  })
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'stockId' implicitly has an 'any' type.
export const deleteStock = stockId => {
  return client.delete(`/stocks/${stockId}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'offerId' implicitly has an 'any' type.
export const cancelEducationalBooking = offerId => {
  return client.patch(`/offers/${offerId}/cancel_booking`)
}

//
// thumbnail
//
// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'url' implicitly has an 'any' type.
export const validateDistantImage = url => {
  return client.post('/offers/thumbnail-url-validation', { url: url })
}

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
// user
//

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'user' implicitly has an 'any' type.
export const signin = user => client.post('/users/signin', user)

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'user' implicitly has an 'any' type.
export const signup = user => client.post('/users/signup/pro', user)

export const signout = () => client.get('/users/signout')

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'body' implicitly has an 'any' type.
export const updateUserInformations = body => {
  return client.patch('/users/current', body)
}

export const getUserInformations = () => {
  return client.get('/users/current')
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'token' implicitly has an 'any' type.
export const validateUser = token => client.patch(`/validate/user/${token}`)

//
// password
//
// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'token' implicitly has an 'any' type.
export const setPassword = (token, newPassword) => {
  return client.post('/users/new-password', { token, newPassword })
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'token' implicitly has an 'any' type.
export const resetPassword = (token, email) => {
  return client.post('/users/reset-password', { token, email })
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'newPassword' implicitly has an 'any' ty... Remove this comment to see the full error message
export const submitResetPassword = (newPassword, token) => {
  return client.post('/users/new-password', { newPassword, token })
}
//
// tutos
//
export const setHasSeenTutos = () => {
  return client.patch(`/users/tuto-seen`)
}

// RGS Banner
//
export const setHasSeenRGSBanner = () => {
  return client.patch(`/users/rgs-seen`)
}

//
// Providers
//
// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueProvider' implicitly has an 'any' ... Remove this comment to see the full error message
export const createVenueProvider = async venueProvider => {
  return client.post('/venueProviders', venueProvider)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'venueProvider' implicitly has an 'any' ... Remove this comment to see the full error message
export const editVenueProvider = async venueProvider => {
  return client.put('/venueProviders', venueProvider)
}

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

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'filters' implicitly has an 'any' type.
export const loadFilteredBookingsRecap = async filters => {
  const queryParams = buildBookingsRecapQuery(filters)
  return client.get(`/bookings/pro?${queryParams}`)
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

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'code' implicitly has an 'any' type.
export const getBooking = code => {
  return client.get(`/v2/bookings/token/${code}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'code' implicitly has an 'any' type.
export const validateBooking = code => {
  return client.patch(`/v2/bookings/use/token/${code}`)
}

// @ts-expect-error ts-migrate(7006) FIXME: Parameter 'code' implicitly has an 'any' type.
export const invalidateBooking = code => {
  return client.patch(`/v2/bookings/keep/token/${code}`)
}

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
// Invoices
//

const buildInvoicesQuery = ({
  businessUnitId = DEFAULT_INVOICES_FILTERS.businessUnitId,
  periodBeginningDate = DEFAULT_INVOICES_FILTERS.periodBeginningDate,
  periodEndingDate = DEFAULT_INVOICES_FILTERS.periodEndingDate,
}) => {
  const params = {}
  if (businessUnitId !== DEFAULT_INVOICES_FILTERS.businessUnitId) {
    // @ts-expect-error ts-migrate(2339) FIXME: Property 'businessUnitId' does not exist on type '... Remove this comment to see the full error message
    params.businessUnitId = businessUnitId
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
