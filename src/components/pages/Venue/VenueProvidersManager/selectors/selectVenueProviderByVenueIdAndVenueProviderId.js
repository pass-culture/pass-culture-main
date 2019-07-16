import createCachedSelector from 're-reselect'

import selectVenueProvidersByVenueId from './selectVenueProvidersByVenueId'

function mapArgsToCacheKey(state, venueId, venueProviderId) {
  return venueProviderId || ''
}

export const selectVenueProviderByVenueIdAndVenueProviderId = createCachedSelector(
  selectVenueProvidersByVenueId,
  (state, venueId) => venueId,
  (state, venueId, venueProviderId) => venueProviderId,
  (venueProviders, venueId, venueProviderId) => {
    const venueProvider =
      venueProviders && venueProviderId && venueProviders.find(vp => vp.id === venueProviderId)
    return Object.assign({ venueId }, venueProvider)
  }
)(mapArgsToCacheKey)

export default selectVenueProviderByVenueIdAndVenueProviderId
