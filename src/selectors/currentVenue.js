import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentOccasion from './currentOccasion'
import selectOccasions from './occasions'
import selectVenues from './venues'

export default createSelector(
  selectVenues,
  (state, ownProps) => ownProps.match.params.venueId,
  selectCurrentOccasion,
  selectOccasions,
  state => state.data.venueProviders,
  (venues, venueId, currentOccasion, occasions,  venueProviders) => {
    console.log('currentOccasion', currentOccasion)
    if (!venues) {
      return
    }

    const venue = venues.find(v =>
      v.id === (venueId || get(currentOccasion, 'venueId')))
    console.log('VENUE', venue)
    if (!venue) {
      return
    }

    const filteredVenueProviders = venueProviders &&
      venueProviders.filter(vp => vp.venueId === venueId)

    if (filteredVenueProviders) {
      filteredVenueProviders.forEach(vp => {
        vp.occasions = occasions && occasions.filter(occasion =>
          occasion.lastProviderId === vp.providerId)
      })
    }
    venue.venueProviders = filteredVenueProviders

    return venue
  }
)
