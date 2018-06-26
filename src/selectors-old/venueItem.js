import get from 'lodash.get'
import groupby from 'lodash.groupby'
import { createSelector } from 'reselect'

import createOccasionsSelect from './createOccasions'
import createVenuesSelect from './createVenues'

export default () => createSelector(
  createVenuesSelect(),
  (state, venueId) => venueId,
  // createOccasionsSelect(),
  (venues, venueId) => {
    return venues.find(v => v.id === venueId.id)
    // if (!venues) {
    //   return
    // }
    // const {
    //   eventOccurences
    // } = (
    //   venues.find(venue => venue.id === venueId) ||
    //   {}
    // )
    // const eventIds = Object.keys(groupby(eventOccurences, 'eventId'))
    // return {
    //   occasions: occasions && occasions.filter(occasion =>
    //     occasion.modelName === 'Event' && eventIds.includes(occasion.id))
    // }
  }
)
