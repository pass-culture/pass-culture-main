import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.events,
  (state, eventId) => eventId,
  (events, eventId) => events.find(event => event.id === eventId)
)
