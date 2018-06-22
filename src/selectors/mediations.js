import get from 'lodash.get'
import { createSelector } from 'reselect'

export default (selectEvent, selectThing) => createSelector(
  state => state.data.mediations,
  selectEvent,
  selectThing,
  (mediations, event, thing) => mediations &&
    mediations.filter(mediation => mediation.eventId === get(event, 'id')
      || mediation.thingId === get(thing, 'id'))
)
