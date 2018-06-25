import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => get(state, 'data.mediations', []),
  (state, params) => params,
  (mediations, {eventId, thingId}) => {
    return mediations.filter(m => m.eventId === eventId && m.thingId === thingId )
  }
)
