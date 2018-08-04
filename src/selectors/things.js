import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.things,
  (state, optionalProviderId) => optionalProviderId,
  (things, optionalProviderId) => {
    if (optionalProviderId) {
      return things.filter(thing => thing.lastProviderId === optionalProviderId)
    }
    return things
  }
)((state, optionalProviderId) => optionalProviderId)
