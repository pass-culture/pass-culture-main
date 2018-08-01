import get from 'lodash.get'
import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

import { THUMBS_URL } from '../utils/config'
import { distanceInMeters } from '../utils/geolocation'

export default createSelector(
  state => state.data.recommendations,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (recommendations, latitude, longitude) => {

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
        venue
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

      // distance
      let distance
      if (!latitude || !longitude || !offer || !venue) {
        distance = '-'
      }
      distance = distanceInMeters(
        latitude,
        longitude,
        venue.latitude,
        venue.longitude
      )
      if (distance < 30) {
        distance = Math.round(distance) + ' m'
      } else if (distance < 100) {
        distance = Math.round(distance / 5) * 5 + ' m'
      } else if (distance < 1000) {
        distance = Math.round(distance / 10) * 10 + ' m'
      } else if (distance < 5000) {
        distance = Math.round(distance / 100) / 10 + ' km'
      } else {
        distance = Math.round(distance / 1000) + ' km'
      }

      return Object.assign({
        distance,
        index,
        thumbUrl
      }, r)

    })

    return filteredRecommendations

  }
)
