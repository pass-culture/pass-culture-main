import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, optionalProviderId) {
  return optionalProviderId
}

const selectThingsByProviderId = createCachedSelector(
  state => state.data.things,
  (state, optionalProviderId) => optionalProviderId,
  (things, optionalProviderId) => {
    if (optionalProviderId) {
      return things.filter(thing => thing.lastProviderId === optionalProviderId)
    }
    return things
  }
)(mapArgsToCacheKey)

export default selectThingsByProviderId
