import get from 'lodash.get'
import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'
// import { Logger } from 'pass-culture-shared'

import { THUMBS_URL } from '../utils/config'
import { distanceInMeters } from '../utils/geolocation'
import { getTimezone } from '../utils/timezone'

export const selectRecommendations = createSelector(
  state => state.data.recommendations,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (recommendations, latitude, longitude) => {
    // RECOMMENDATION MUST HAVE MEDIATION AND/OR OFFER CHILDREN
    // AND THAT IS A CRITERION TO MAKE THEM UNIQ
    let filteredRecommendations = recommendations.map(recommendation => {
      const { mediation, offer } = recommendation
      const { eventId, thingId } = offer || {}
      const { tutoIndex } = mediation || {}
      let uniqId
      if (eventId) {
        uniqId = `event_${eventId}`
      } else if (thingId) {
        uniqId = `thing_${thingId}`
      } else if (typeof tutoIndex !== 'undefined') {
        uniqId = `tuto_${tutoIndex}`
      }
      return Object.assign({ uniqId }, recommendation)
    })
    filteredRecommendations = filteredRecommendations.filter(
      recommendation => recommendation.uniqId
    )
    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.uniqId
    )

    // NOW WE CAN GIVE OTHER PROPERTIES TO THE GOOD SHAPED RECO
    filteredRecommendations = filteredRecommendations.map(
      (recommendation, index) => {
        const { mediation, offer } = recommendation
        const { eventOrThing, eventId, thingId, venue } = offer || {}

        // thumbUrl
        let thumbUrl
        let firstThumbDominantColor
        const mediationId = get(mediation, 'id')
        if (
          mediationId
          // && get(mediation, 'thumbCount')
        ) {
          thumbUrl = `${THUMBS_URL}/mediations/${mediationId}`
          firstThumbDominantColor = get(mediation, 'firstThumbDominantColor')
        } else if (
          eventId
          //  && get(offer, 'eventOrThing.thumbCount')
        ) {
          thumbUrl = `${THUMBS_URL}/events/${eventId}`
          firstThumbDominantColor = get(eventOrThing, 'firstThumbDominantColor')
        } else {
          thumbUrl =
            thingId &&
            // && get(offer, 'eventOrThing.thumbCount')
            `${THUMBS_URL}/things/${thingId}`
          firstThumbDominantColor = get(eventOrThing, 'firstThumbDominantColor')
        }

        // distance
        let distance
        if (!latitude || !longitude || !offer || !venue) {
          distance = '-'
        } else {
          distance = distanceInMeters(
            latitude,
            longitude,
            venue.latitude,
            venue.longitude
          )
          if (distance < 30) {
            distance = `${Math.round(distance)} m`
          } else if (distance < 100) {
            distance = `${Math.round(distance / 5) * 5} m`
          } else if (distance < 1000) {
            distance = `${Math.round(distance / 10) * 10} m`
          } else if (distance < 5000) {
            distance = `${Math.round(distance / 100) / 10} km`
          } else {
            distance = `${Math.round(distance / 1000)} km`
          }
        }

        // timezone
        const tz = getTimezone(get(venue, 'departementCode'))

        // return
        return Object.assign(
          {
            distance,
            firstThumbDominantColor,
            index,
            thumbUrl,
            tz,
          },
          recommendation
        )
      }
    )

    return filteredRecommendations
  }
)

export default selectRecommendations
