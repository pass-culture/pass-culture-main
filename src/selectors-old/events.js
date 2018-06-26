import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.events,
  state => state.data.searchedEvents,
  state => state.data.eventOccurences,
  state => state.data.mediations,
  state => state.data.venues,
  (events, searchedEvents, eventOccurences, mediations, venues) => {
    if (!events && !searchedEvents) return

    // priority to searched elements
    const filteredEvents = [...(searchedEvents || events)]

    // refill the objects from their join objects
    // but removed during the normalizer time
    filteredEvents.forEach(event => {

        // OCCURENCES
        const occurences = (eventOccurences && eventOccurences.filter(
          eo => eo.eventId === event.id
        )) || []
        occurences.forEach(event => {
          event.beginningDatetimeMoment = moment(event.beginningDatetime)
        })
        occurences.sort((event1,event2) =>
          event1.beginningDatetimeMoment - event2.beginningDatetimeMoment)
        event.occurences = occurences

        // VENUE
        const venueId = get(occurences, '0.venueId')
        const venue = venueId && venues && venues.find(venue =>
          venue.id === venueId)
        event.venue = venue
        event.venueId = venueId

        // OFFERER
        event.offererId = get(venue, 'managingOffererId')

        // MEDIATIONS
        event.mediations = (mediations && mediations.filter(
          mediation => mediation.eventId === event.id
        )) || []

    })

    return filteredEvents
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
