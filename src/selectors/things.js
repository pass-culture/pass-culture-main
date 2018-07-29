import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.things,
  (state, providerId) => providerId,
  (things, providerId) => {
    if (providerId) {
      return things.filter(thing => thing.lastProviderId === providerId)
    }
    return things
  }
)((state, providerId) => providerId)
