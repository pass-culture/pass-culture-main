import { createSelector } from 'reselect'

const emptyEventOccurences = []

export default () => createSelector(
  state => state.data.eventOccurences,
  (state, ownProps) => ownProps.venue.id,
  (eventOccurences, venueId) =>
    (eventOccurences && eventOccurences.filter(eo => eo.venueId === venueId)) ||
    emptyOffers
)
