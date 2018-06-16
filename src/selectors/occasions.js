import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  state => state.data.eventOccurences,
  state => state.data.mediations,
  (occasions, searchedOccasions, eventOccurences, mediations) => {
    if (!occasions && !searchedOccasions) return

    // priority to searched elements
    const filteredOccasions = [...(searchedOccasions || occasions)]

    // refill the objects from their join objects
    // but removed during the normalizer time
    filteredOccasions.forEach(o => {

        // OCCURENCES
        const occurences = eventOccurences && eventOccurences.filter(
          eo => eo.eventId === o.id
        )
        if (occurences) {
          occurences.forEach(o => {
            o.beginningDatetimeMoment = moment(o.beginningDatetime)
          })
          occurences.sort((o1,o2) =>
            o1.beginningDatetimeMoment - o2.beginningDatetimeMoment)
        }
        o.occurences = occurences

        // VENUE
        o.venueId = get(occurences, '0.venueId')

        // OFFERER
        o.offererId = get(occurences, '0.venue.managingOffererId')

        // MEDIATIONS
        o.mediations = mediations && mediations.filter(
          eo => eo.eventId === o.id
        )

    })

    return filteredOccasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
