import { DEFAULT_PRE_FILTERS } from 'components/pages/Bookings/PreFilters/_constants'
import { ALL_OFFERERS, DEFAULT_SEARCH_FILTERS } from 'components/pages/Offers/Offers/_constants'
import { client } from 'repository/pcapi/pcapiClient'
import { FORMAT_ISO_DATE_ONLY, formatBrowserTimezonedDateAsUTC } from 'utils/date'
import { stringify } from 'utils/query-string'

export const loadFeatures = async () => {
  return client.get('/features')
}

//
// offers
//
export const loadOffer = async offerId => {
  return client.get(`/offers/${offerId}`)
}

export const createOffer = offer => {
  return client.post(`/offers`, offer)
}

export const updateOffer = (offerId, offer) => {
  return client.patch(`/offers/${offerId}`, offer)
}

export const loadFilteredOffers = async ({
  name = DEFAULT_SEARCH_FILTERS.name,
  offererId = DEFAULT_SEARCH_FILTERS.offererId,
  venueId = DEFAULT_SEARCH_FILTERS.venueId,
  typeId = DEFAULT_SEARCH_FILTERS.typeId,
  periodBeginningDate = DEFAULT_SEARCH_FILTERS.periodBeginningDate,
  periodEndingDate = DEFAULT_SEARCH_FILTERS.periodEndingDate,
  status = DEFAULT_SEARCH_FILTERS.status,
  creationMode = DEFAULT_SEARCH_FILTERS.creationMode,
}) => {
  const body = createRequestBody({
    name,
    offererId,
    venueId,
    typeId,
    status,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
  })

  const queryParams = stringify(body)
  return client.get(`/offers${queryParams ? `?${queryParams}` : ''}`)
}

export const updateOffersActiveStatus = (
  areAllOffersSelected,
  {
    name = DEFAULT_SEARCH_FILTERS.name,
    offererId = DEFAULT_SEARCH_FILTERS.offererId,
    venueId = DEFAULT_SEARCH_FILTERS.venueId,
    typeId = DEFAULT_SEARCH_FILTERS.typeId,
    status = DEFAULT_SEARCH_FILTERS.status,
    creationMode = DEFAULT_SEARCH_FILTERS.creationMode,
    ids = [],
    isActive,
    periodBeginningDate = DEFAULT_SEARCH_FILTERS.periodBeginningDate,
    periodEndingDate = DEFAULT_SEARCH_FILTERS.periodEndingDate,
  }
) => {
  const formattedBody = createRequestBody({
    name,
    offererId,
    venueId,
    typeId,
    status,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
  })

  if (areAllOffersSelected) {
    return client.patch('/offers/all-active-status', { ...formattedBody, isActive })
  }

  return client.patch('/offers/active-status', { ids, isActive })
}

const createRequestBody = searchFilters => {
  const body = {}
  Object.keys(DEFAULT_SEARCH_FILTERS).forEach(field => {
    if (searchFilters[field] && searchFilters[field] !== DEFAULT_SEARCH_FILTERS[field]) {
      body[field] = searchFilters[field]
    }
  })

  if (searchFilters.page) {
    body.page = searchFilters.page
  }

  if (searchFilters.periodBeginningDate !== DEFAULT_SEARCH_FILTERS.periodBeginningDate) {
    body.periodBeginningDate = searchFilters.periodBeginningDate
  }

  if (searchFilters.periodEndingDate !== DEFAULT_SEARCH_FILTERS.periodEndingDate) {
    body.periodEndingDate = searchFilters.periodEndingDate
  }

  return body
}

export const getAllOfferersNames = () => {
  return client.get('/offerers/names').then(response => response.offerersNames)
}

export const generateOffererApiKey = async offererId => {
  return client.post(`/offerers/${offererId}/api_keys`, {}).then(response => response.apiKey)
}

export const getUserValidatedOfferersNames = () => {
  return client
    .get('/offerers/names?validated_for_user=true')
    .then(response => response.offerersNames)
}

export const getValidatedOfferersNames = () => {
  return client.get('/offerers/names?validated=true').then(response => response.offerersNames)
}

export const getOfferers = () => {
  return client.get('/offerers')
}

export const getValidatedOfferers = () => {
  return client.get('/offerers?validated=true')
}

export const getOfferer = offererId => {
  return client.get(`/offerers/${offererId}`)
}

//
// venues
//
export const getVenuesForOfferer = ({ offererId = null, activeOfferersOnly = false } = {}) => {
  const request = {}
  if (offererId) {
    if (offererId !== ALL_OFFERERS) request.offererId = offererId
  } else {
    request.validatedForUser = true
  }

  if (activeOfferersOnly) request.activeOfferersOnly = true
  const queryParams = stringify(request)
  const url = queryParams !== '' ? `/venues?${queryParams}` : '/venues'
  return client.get(url).then(response => response.venues)
}

export const getVenue = venueId => client.get(`/venues/${venueId}`)

export const getVenueStats = venueId => client.get(`/venues/${venueId}/stats`)

export const getOffererWithVenueStats = offererId => client.get(`/offerers/${offererId}/stats`)

//
// types
//
export const loadTypes = () => {
  return client.get('/types')
}

//
// stocks
//
export const loadStocks = offerId => {
  return client.get(`/offers/${offerId}/stocks`)
}

export const bulkCreateOrEditStock = (offerId, stocks) => {
  return client.post(`/stocks/bulk`, {
    offerId,
    stocks,
  })
}

export const deleteStock = stockId => {
  return client.delete(`/stocks/${stockId}`)
}

//
// thumbnail
//
export const validateDistantImage = url => {
  return client.post('/offers/thumbnail-url-validation', { url: url })
}

export const postThumbnail = (offerer, offer, credit, thumb, thumbUrl, x, y, height) => {
  const body = new FormData()
  body.append('offerId', offer)
  body.append('offererId', offerer)
  body.append('credit', credit)
  body.append('croppingRectX', x)
  body.append('croppingRectY', y)
  body.append('croppingRectHeight', height)
  body.append('thumb', thumb)
  body.append('thumbUrl', thumbUrl)

  return client.postWithFormData('/offers/thumbnails', body)
}

//
// user
//
export const signout = () => client.get('/users/signout')

export const updateUserInformations = body => {
  return client.patch('/users/current', body)
}

//
// set password
//
export const setPassword = (token, newPassword) => {
  return client.post('/users/new-password', { token, newPassword })
}

//
// tutos
//
export const setHasSeenTutos = () => {
  return client.patch(`/users/tuto-seen`)
}

//
// Providers
//
export const createVenueProvider = async venueProvider => {
  return client.post('/venueProviders', venueProvider)
}

export const loadProviders = async venueId => {
  return client.get(`/providers/${venueId}`)
}

export const loadVenueProviders = async venueId => {
  return client.get(`/venueProviders?venueId=${venueId}`).then(response => response.venue_providers)
}

//
// BookingsRecap
//
export const loadFilteredBookingsRecap = async ({
  venueId = DEFAULT_PRE_FILTERS.offerVenueId,
  eventDate = DEFAULT_PRE_FILTERS.offerEventDate,
  bookingPeriodBeginningDate = DEFAULT_PRE_FILTERS.bookingBeginningDate,
  bookingPeriodEndingDate = DEFAULT_PRE_FILTERS.bookingEndingDate,
  page,
}) => {
  const params = { page }
  if (venueId !== DEFAULT_PRE_FILTERS.offerVenueId) {
    params.venueId = venueId
  }
  if (eventDate !== DEFAULT_PRE_FILTERS.offerEventDate) {
    params.eventDate = formatBrowserTimezonedDateAsUTC(eventDate)
  }
  params.bookingPeriodBeginningDate = formatBrowserTimezonedDateAsUTC(
    bookingPeriodBeginningDate,
    FORMAT_ISO_DATE_ONLY
  )
  params.bookingPeriodEndingDate = formatBrowserTimezonedDateAsUTC(
    bookingPeriodEndingDate,
    FORMAT_ISO_DATE_ONLY
  )

  const queryParams = stringify(params)
  return client.get(`/bookings/pro?${queryParams}`)
}

//
// Booking
//

export const getBooking = code => {
  return client.get(`/v2/bookings/token/${code}`)
}

export const validateBooking = code => {
  return client.patch(`/v2/bookings/use/token/${code}`)
}

export const invalidateBooking = code => {
  return client.patch(`/v2/bookings/keep/token/${code}`)
}
