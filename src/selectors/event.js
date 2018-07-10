import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.events,
  (state, eventId) => eventId,
  (events, eventId) => events.find(event => event.id === eventId)
)(
  (state, eventId) => eventId || ''
)
