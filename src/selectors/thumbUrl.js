import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import { THUMBS_URL } from '../utils/config'

import mediationsSelector from './mediations'
import eventSelector from './event'
import thingSelector from './thing'

export default createCachedSelector(
  (state, eventId, thingId) => mediationsSelector(state, eventId, thingId),
  (state, eventId, thingId) => eventSelector(state, eventId),
  (state, eventId, thingId) => thingSelector(state, thingId),
  (mediations, event, thing) =>
    get(mediations, '0')
      ? `${THUMBS_URL}/mediations/${mediations[0].id}`
      : get(event, 'thumbCount')
        ? `${THUMBS_URL}/events/${get(event, 'id')}`
        : get(thing, 'thumbCount') && `${THUMBS_URL}/things/${get(thing, 'id')}`
)(
  (state, eventId, thingId) => `${eventId || ''}/${thingId || ''}`
)
