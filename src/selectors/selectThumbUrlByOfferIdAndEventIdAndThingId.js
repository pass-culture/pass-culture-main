import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import selectActiveMediationsByOfferId from './selectActiveMediationsByOfferId'
import selectEventById from './selectEventById'
import selectThingById from './selectThingById'
import { THUMBS_URL } from '../utils/config'

function mapArgsToCacheKey(state, offerId, eventId, thingId) {
  return `${offerId || ''}/${eventId || ''}/${thingId || ''}`
}

export const selectThumbUrlByOfferIdAndEventIdAndThingId = createCachedSelector(
  (state, offerId, eventId, thingId) =>
    selectActiveMediationsByOfferId(state, offerId),
  (state, offerId, eventId, thingId) => selectEventById(state, eventId),
  (state, offerId, eventId, thingId) => selectThingById(state, thingId),
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
)(mapArgsToCacheKey)

export default selectThumbUrlByOfferIdAndEventIdAndThingId
