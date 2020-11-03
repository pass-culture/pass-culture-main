import {
  ALL_OFFERS,
  ALL_OFFERERS,
  ALL_VENUES,
  ALL_TYPES,
  DEFAULT_PAGE,
} from 'components/pages/Offers/_constants'
import { client } from 'repository/pcapi/pcapiClient'

//
// offers
//
export const loadOffer = async offerId => {
  return client.get(`/offers/${offerId}`)
}

export const loadFilteredOffers = async ({
  nameSearchValue = ALL_OFFERS,
  offererId = ALL_OFFERERS,
  selectedVenueId = ALL_VENUES,
  selectedTypeId = ALL_TYPES,
  page = DEFAULT_PAGE,
}) => {
  const body = createRequestBody(nameSearchValue, offererId, selectedVenueId, selectedTypeId, page)
  const queryParams = new URLSearchParams(body).toString()
  return client.get(`/offers?${queryParams}`)
}

export const updateOffersActiveStatus = (
  areAllOffersSelected,
  {
    name = ALL_OFFERS,
    offererId = ALL_OFFERERS,
    venueId = ALL_VENUES,
    typeId = ALL_TYPES,
    page = DEFAULT_PAGE,
    ids = [],
    isActive,
  }
) => {
  const formattedBody = createRequestBody(name, offererId, venueId, typeId, page)

  if (areAllOffersSelected) {
    return client.patch('/offers/all-active-status', { ...formattedBody, isActive })
  }

  return client.patch('/offers/active-status', { ids, isActive })
}

const createRequestBody = (nameSearchValue, offererId, selectedVenueId, selectedTypeId, page) => {
  const body = {}
  if (nameSearchValue !== ALL_OFFERS) {
    body.name = nameSearchValue
  }
  if (offererId !== ALL_OFFERERS) {
    body.offererId = offererId
  }
  if (selectedVenueId !== ALL_VENUES) {
    body.venueId = selectedVenueId
  }
  if (selectedTypeId !== ALL_TYPES) {
    body.typeId = selectedTypeId
  }
  if (page) {
    body.page = page
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
