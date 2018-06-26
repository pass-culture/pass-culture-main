import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.events,
  (state, params) => params,
  (events, eventId) => events.find(event => event.id === eventId)
)
