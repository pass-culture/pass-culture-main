import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.things,
  state => state.data.searchedThings,
  state => state.data.mediations,
  state => state.data.venues,
  (things, searchedThings, mediations, venues) => {
    if (!things && !searchedThings) return

    // priority to searched elements
    const filteredThings = [...(searchedThings || things)]

    // refill the objects from their join objects
    // but removed during the normalizer time
    filteredThings.forEach(thing => {

        // TODO: find the VENUE

        // TODO: find the OFFERER

        // MEDIATIONS
        thing.mediations = (mediations && mediations.filter(
          mediation => mediation.thingId === thing.id
        )) || []

    })

    return filteredThings
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
