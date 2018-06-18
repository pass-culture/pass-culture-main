import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  state => state.data.eventOccurences,
  state => state.data.mediations,
  state => state.data.venues,
  (occasions, searchedOccasions, eventOccurences, mediations, venues) => {
    if (!occasions && !searchedOccasions) return

    // priority to searched elements
    const filteredOccasions = [...(searchedOccasions || occasions)]

    // refill the objects from their join objects
    // but removed during the normalizer time
    filteredOccasions.forEach(occasion => {

        // OCCURENCES
        const occurences = (eventOccurences && eventOccurences.filter(
          eo => eo.eventId === occasion.id
        )) || []
        occurences.forEach(occasion => {
          occasion.beginningDatetimeMoment = moment(occasion.beginningDatetime)
        })
        occurences.sort((occasion1,occasion2) =>
          occasion1.beginningDatetimeMoment - occasion2.beginningDatetimeMoment)
        occasion.occurences = occurences

        // VENUE
        const venueId = get(occurences, '0.venueId')
        const venue = venueId && venues && venues.find(venue =>
          venue.id === venueId)
        occasion.venue = venue
        occasion.venueId = venueId

        // OFFERER
        occasion.offererId = get(venue, 'managingOffererId')

        // MEDIATIONS
        occasion.mediations = (mediations && mediations.filter(
          mediation => mediation.eventId === occasion.id
        )) || []

    })

    return filteredOccasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
