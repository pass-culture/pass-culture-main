import createCachedSelector from 're-reselect'

import venueProvidersSelector from './venueProviders'

export default createCachedSelector(
  venueProvidersSelector,
  (state, venueId) => venueId,
  (state, venueId, venueProviderId) => venueProviderId,
  (venueProviders, venueId, venueProviderId) => {
    const venueProvider = venueProviders && venueProviderId &&
      venueProviders.find(vp => vp.id === venueProviderId)
    return Object.assign({ venueId }, venueProvider)
  }
)(
  (state, venueId, venueProviderId) => venueProviderId || ''
)
