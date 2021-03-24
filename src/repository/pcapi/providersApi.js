import { client } from './pcapiClient'

export const createVenueProvider = async venueProvider => {
  return client.post('/venueProviders', venueProvider)
}

export const loadProviders = async venueId => {
  return client.get(`/providers/${venueId}`)
}

export const loadVenueProviders = async venueId => {
  return client.get(`/venueProviders?venueId=${venueId}`)
}
