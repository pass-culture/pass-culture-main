import get from 'lodash.get'
import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

import { THUMBS_URL } from '../utils/config'

export default createSelector(
  state => state.data.recommendations,
  recommendations => {

    let filteredRecommendations = uniqBy(recommendations, recommendation => {
      const {
        mediation,
        offer
      } = recommendation
      const {
        eventId,
        thingId,
      } = (offer || {})
      const {
        tutoIndex
      } = (mediation || {})
      if (eventId) {
        return `event_${eventId}`
      }
      if (thingId) {
        return `thing_${thingId}`
      }
      if (tutoIndex) {
        return `tuto_${tutoIndex}`
      }
      console.warn('weird this recommendation is with no thing or event or tuto')
      return ''
    })

    filteredRecommendations = filteredRecommendations.map((r, index) => {

      const {
        mediation,
        offer
      } = r
      const {
        eventId,
        thingId,
      } = (offer || {})

      // thumbUrl
      let thumbUrl
      const mediationId = get(mediation, 'id')
      if (mediationId
        // && get(mediation, 'thumbCount')
      ) {
        thumbUrl = `${THUMBS_URL}/mediations/${mediationId}`
      } else {
        if (eventId
          //  && get(offer, 'eventOrThing.thumbCount')
        ) {
          thumbUrl = `${THUMBS_URL}/events/${eventId}`
        } else {
          thumbUrl = thingId
            // && get(offer, 'eventOrThing.thumbCount')
            && `${THUMBS_URL}/things/${thingId}`
        }
      }

      return Object.assign({
        index,
        thumbUrl
      }, r)

    })

    return filteredRecommendations

  }
)
