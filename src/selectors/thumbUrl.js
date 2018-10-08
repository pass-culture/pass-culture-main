import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import selectActiveMediationsByOfferId from './selectActiveMediationsByOfferId'
import eventSelector from './event'
import thingSelector from './thing'
import { THUMBS_URL } from '../utils/config'

function mapArgsToKey(state, offerId, eventId, thingId) {
  return `${offerId || ''}/${eventId || ''}/${thingId || ''}`
}

export default createCachedSelector(
  (state, offerId, eventId, thingId) =>
    selectActiveMediationsByOfferId(state, offerId),
  (state, offerId, eventId, thingId) => eventSelector(state, eventId),
  (state, offerId, eventId, thingId) => thingSelector(state, thingId),
  (mediations, event, thing) => {
    if (get(mediations, '0')) {
      return `${THUMBS_URL}/mediations/${mediations[0].id}`
    }

    if (get(event, 'thumbCount')) {
      return `${THUMBS_URL}/events/${get(event, 'id')}`
    }

    return (
      get(thing, 'thumbCount') && `${THUMBS_URL}/things/${get(thing, 'id')}`
    )
  }
)(mapArgsToKey)
