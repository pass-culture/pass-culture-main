import get from 'lodash.get'
import { createSelector } from 'reselect'

import { selectCurrentOccasion } from './occasion'
import selectOccasions from './occasions'
import { selectVenues } from './venues'

const createSelectVenue = selectOccasion => createSelector(
  selectVenues,
  (state, ownProps) => get(ownProps, 'match.params.venueId'),
  selectOccasion,
  selectOccasions,
  state => state.data.venueProviders,
  (venues, venueId, occasion, occasions, venueProviders) => {
    if (!venues) {
      return
    }

    console.log('venues', venues, occasion, get(occasion, 'venueId'))

    const venue = venues.find(v =>
      v.id === (venueId || get(occasion, 'venueId')))

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
export default createSelectVenue

export const selectCurrentVenue = createSelectVenue(selectCurrentOccasion)
