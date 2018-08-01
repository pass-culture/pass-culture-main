import get from 'lodash.get'
import { createSelector } from 'reselect'

import currentMediationSelector from './currentMediation'
import currentOfferSelector from './currentOffer'
// import getThumbUrl from '../getters/thumbUrl'
import { THUMBS_URL } from '../utils/config'

export default createSelector(
  currentMediationSelector,
  currentOfferSelector,
  (currentMediation, currentOffer) => {

    const currentMediationId = get(currentMediation, 'id')
    if (currentMediationId && get(currentMediation, 'thumbCount')) {
      return `${THUMBS_URL}/mediations/${currentMediationId}`
    }

    const currentEventId = get(currentOffer, 'eventId')
    if (currentEventId && get(currentOffer, 'eventOrThing.thumbCount')) {
      return `${THUMBS_URL}/events/${currentEventId}`
    }

    const currentThingId = get(currentOffer, 'thingId')
    return currentThingId &&
      get(currentOffer, 'eventOrThing.thumbCount') &&
      `${THUMBS_URL}/things/${currentThingId}`

  }
)
