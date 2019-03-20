import createCachedSelector from 're-reselect'

function mapArgToKey(state, optionalProviderId) {
  return optionalProviderId
}

export const selectThingsByProviderId = createCachedSelector(
  state => state.data.things,
  (state, optionalProviderId) => optionalProviderId,
  (things, optionalProviderId) => {
    if (optionalProviderId) {
      return things.filter(thing => thing.lastProviderId === optionalProviderId)
    }
    return things
  }
)(mapArgToKey)

export default selectThingsByProviderId
