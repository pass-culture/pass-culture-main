import { DEFAULT_SEARCH_FILTERS, DEFAULT_PAGE } from 'components/pages/Offers/_constants'
import { client } from 'repository/pcapi/pcapiClient'

//
// offers
//
export const loadOffer = async offerId => {
  return client.get(`/offers/${offerId}`)
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

  const queryParams = new URLSearchParams(body).toString()
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

export const setAllVenueOffersActivate = async venueId => {
  return client.put(`/venues/${venueId}/offers/activate`)
}

export const setAllVenueOffersInactivate = async venueId => {
  return client.put(`/venues/${venueId}/offers/deactivate`)
}

//
// types
//
export const loadTypes = () => {
  return client.get(`/types`)
}
