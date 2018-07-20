import createCachedSelector from 're-reselect'
import {resolveDataCollection} from '../utils/resolvers'

export default createCachedSelector(
  state => state.data.events,
  (state, providerId) => providerId,
  (events, providerId) => {
    events = resolveDataCollection(events, 'events')
    if (providerId) {
      events = events.filter(event => event.lastProviderId === providerId)
    }
    return events
  }
)(
  (state, providerId) => providerId || ''
)
