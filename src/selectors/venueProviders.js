import createCachedSelector from 're-reselect';

export default createCachedSelector(
  state => state.data.venueProviders,
  (state, optionalVenueId) => optionalVenueId,
  (venueProviders, optionalVenueId) => {
    if (optionalVenueId)
      venueProviders = venueProviders.filter(vp => vp.venueId === optionalVenueId)
    return venueProviders
  }
)(
  (state, optionalVenueId) => optionalVenueId || '',
)
