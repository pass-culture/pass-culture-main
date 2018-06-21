import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectTypes from './types'

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  state => state.data.events,
  state => state.data.eventOccurences,
  state => state.data.mediations,
  state => state.data.things,
  state => state.data.venues,
  selectTypes,
  (
    occasions,
    searchedOccasions,
    events,
    eventOccurences,
    mediations,
    things,
    venues,
    types
  ) => {
    if (!occasions && !searchedOccasions) return

    // priority to searched elements
    const filteredOccasions = [...(searchedOccasions || occasions)]

    // refill the objects from their join objects
    // but removed during the normalizer time
    filteredOccasions.forEach(occasion => {

      // EVENTS
      if (occasion.eventId) {
        const event = events && events.find(event => event.id === occasion.eventId)
        occasion.event = event

        if (event) {
          // OCCURENCES
          const occurences = (eventOccurences && eventOccurences.filter(
            eo => eo.eventId === occasion.id
          )) || []
          occurences.forEach(occurence => {
            occurence.beginningDatetimeMoment = moment(occurence.beginningDatetime)
          })
          occurences.sort((event1,event2) =>
            event1.beginningDatetimeMoment - event2.beginningDatetimeMoment)
          event.occurences = occurences

          // MEDIATIONS
          event.mediations = (mediations && mediations.filter(
            mediation => mediation.eventId === occasion.id ||
              mediation.thingId === occasion.id
          )) || []

          // TYPE
          event.typeOption = types && types.find(type =>
            type.tag === event.type)
        }
      }

      // THINGS
      if (occasion.thingId) {
        const thing = things && things.find(thing => thing.id === occasion.thingId)
        occasion.thing = thing

        if (thing) {

          // MEDIATIONS
          thing.mediations = (mediations && mediations.filter(
            mediation => mediation.thingId === occasion.id ||
              mediation.thingId === occasion.id
          )) || []

          // TYPE
          thing.typeOption = types && types.find(type =>
            type.tag === thing.type)
        }
      }

      // VENUE
      const venue = venues && venues.find(venue =>
        venue.id === occasion.venueId)
      occasion.venue = venue

    })

    return filteredOccasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
