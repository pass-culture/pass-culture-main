import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, providerId) {
  return providerId || ''
}

const selectEventsByProviderId = createCachedSelector(
  state => state.data.events,
  (state, providerId) => providerId,
  (events, providerId) => events.filter(event => event.lastProviderId === providerId)
)(mapArgsToCacheKey)

export default selectEventsByProviderId
