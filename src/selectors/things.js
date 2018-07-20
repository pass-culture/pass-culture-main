import createCachedSelector from 're-reselect'

import {resolveDataCollection} from '../utils/resolvers'

export default createCachedSelector(
  state => state.data.things,
  (state, providerId) => providerId,
  (things, providerId) => {
    things = resolveDataCollection(things, 'things')
    if (providerId) {
      return things.filter(thing => thing.lastProviderId === providerId)
    }
    return things
  }
)(
  (state, providerId) => providerId
)
