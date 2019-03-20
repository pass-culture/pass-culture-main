import createCachedSelector from 're-reselect'

function mapArgToKey(state, providerId) {
  return providerId || ''
}

export const selectEventsByProviderId = createCachedSelector(
  state => state.data.events,
  (state, providerId) => providerId,
  (events, providerId) =>
    events.filter(event => event.lastProviderId === providerId)
)(mapArgToKey)

export default selectEventsByProviderId
