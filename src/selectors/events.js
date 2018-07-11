import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.events,
  (state, providerId) => providerId,
  (events, providerId) => {
    if (!events) {
      return
    }
    if (providerId) {
      return events.filter(event => event.lastProviderId === providerId)
    }
    return events
  }
)(
  (state, providerId) => providerId
)
