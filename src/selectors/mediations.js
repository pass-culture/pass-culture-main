import createCachedSelector from 're-reselect'
import {resolveDataCollection} from '../utils/resolvers'

export default createCachedSelector(
  state => state.data.mediations,
  (state, optionalEventId, optionalThingId) => optionalEventId,
  (state, optionalEventId, optionalThingId) => optionalThingId,
  (mediations, optionalEventId, optionalThingId) => {
    mediations = resolveDataCollection(mediations, 'mediations')
    if (optionalEventId)
      mediations = mediations.filter(m => m.eventId === optionalEventId)

    if (optionalThingId)
      mediations = mediations.filter(m => m.thingId === optionalThingId)

    return mediations
  }
)(
  (state, optionalEventId, optionalThingId) => `${optionalEventId || ''}/${optionalThingId || ''}`
)
