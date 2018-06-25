import get from 'lodash.get'
import groupby from 'lodash.groupby'
import { createSelector } from 'reselect'

import selectOccasions from './occasions'
import createSelectVenues from './venues'

export default () => createSelector(
  createSelectVenues(),
  (state, ownProps) => get(ownProps, 'venue.id'),
  selectOccasions,
  (venues, venueId, occasions) => {
    if (!venues) {
      return
    }
    const {
      eventOccurences
    } = (
      venues.find(venue => venue.id === venueId) ||
      {}
    )
    const eventIds = Object.keys(groupby(eventOccurences, 'eventId'))
    return {
      occasions: occasions && occasions.filter(occasion =>
        occasion.modelName === 'Event' && eventIds.includes(occasion.id))
    }
  }
)
