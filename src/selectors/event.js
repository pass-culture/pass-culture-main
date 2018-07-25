import createCachedSelector from 're-reselect'

import eventsSelector from './events'

export default createCachedSelector(
  state => eventsSelector(state),
  (state, eventId) => eventId,
  (events, eventId) => events.find(event => event.id === eventId)
)(
  (state, eventId) => eventId || ''
)
