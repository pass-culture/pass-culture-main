import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.venues,
  state => state.data.eventOccurences,
  (venues, eventOccurences) => {
    if (!venues) return

    // clone
    const filteredVenues = [...venues]

    // refill the objects from their join objects
    // but removed during the normalizer time
    filteredVenues.forEach(venue => {

        // OCCURENCES
        venue.eventOccurences = (eventOccurences && eventOccurences.filter(
          eo => eo.venueId === venue.id
        )) || []

    })

    return filteredVenues
  }
)
