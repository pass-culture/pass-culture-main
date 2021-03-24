import { createSelector } from 'reselect'

export const selectVenueProvidersByVenueId = createSelector(
  state => state.data.venueProviders,
  (state, optionalVenueId) => optionalVenueId,
  (venueProviders, optionalVenueId) => {
    if (optionalVenueId)
      venueProviders = venueProviders.filter(vp => vp.venueId === optionalVenueId)
    return venueProviders
  }
)
