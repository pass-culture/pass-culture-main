import {
  ALL_OFFERS,
  ALL_OFFERERS,
  ALL_VENUES,
  ALL_TYPES,
  ALL_STATUS,
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
  status = ALL_STATUS,
}) => {
  const body = createRequestBody(nameSearchValue, offererId, selectedVenueId, selectedTypeId, page, status)
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
    status = ALL_STATUS,
  }
) => {
  const formattedBody = createRequestBody(name, offererId, venueId, typeId, page, status)

  if (areAllOffersSelected) {
    return client.patch('/offers/all-active-status', { ...formattedBody, isActive })
  }

  return client.patch('/offers/active-status', { ids, isActive })
}

const createRequestBody = (nameSearchValue, offererId, selectedVenueId, selectedTypeId, page, status) => {
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
  if (status !== ALL_STATUS) {
    body.status = status
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
