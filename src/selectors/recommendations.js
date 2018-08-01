import get from 'lodash.get'
import { createSelector } from 'reselect'

import { THUMBS_URL } from '../utils/config'

export default createSelector(
  state => state.data.recommendations,
  recommendations =>
    recommendations.map((r, index) => {

      const {
        mediation,
        offer
      } = r

      // thumbUrl
      let thumbUrl
      const mediationId = get(mediation, 'id')
      if (mediationId && get(mediation, 'thumbCount')) {
        thumbUrl = `${THUMBS_URL}/mediations/${mediationId}`
      } else {

        const eventId = get(offer, 'eventId')
        if (eventId && get(offer, 'eventOrThing.thumbCount')) {
          thumbUrl = `${THUMBS_URL}/events/${eventId}`
        } else {

          const thingId = get(offer, 'thingId')
          thumbUrl = thingId &&
            get(offer, 'eventOrThing.thumbCount') &&
            `${THUMBS_URL}/things/${thingId}`

        }
      }

      return Object.assign({
        index,
        thumbUrl
      }, r)

    })
)
