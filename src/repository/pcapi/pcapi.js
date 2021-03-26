import { DEFAULT_PAGE, DEFAULT_SEARCH_FILTERS } from 'components/pages/Offers/Offers/_constants'
import { client } from 'repository/pcapi/pcapiClient'
import { stringify } from 'utils/query-string'

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
  page = DEFAULT_PAGE,
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
    page,
    status,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
  })

  const queryParams = stringify(body)
  return client.get(`/offers?${queryParams}`)
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
    page = DEFAULT_PAGE,
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
    page,
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
export const setAllVenueOffersActivate = async venueId => {
  return client.put(`/venues/${venueId}/offers/activate`)
}

export const setAllVenueOffersInactivate = async venueId => {
  return client.put(`/venues/${venueId}/offers/deactivate`)
}

export const getVenuesForOfferer = offererId => {
  if (offererId) {
    return client.get(`/venues?offererId=${offererId}`)
  } else {
    return client.get('/venues?validated_for_user=true')
  }
}

export const getVenue = venueId => client.get(`/venues/${venueId}`)

export const getVenueStats = venueId => client.get(`/venues/${venueId}/stats`)

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
export const setHasSeenTutos = userId => {
  return client.patch(`/users/${userId}/tuto-seen`)
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
  return client.get(`/venueProviders?venueId=${venueId}`)
}
