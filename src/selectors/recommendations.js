import get from 'lodash.get'
import uniqBy from 'lodash.uniqby'
import { createSelector } from 'reselect'

import { ROOT_PATH, THUMBS_URL } from '../utils/config'
import { computeDistanceInMeters, humanizeDistance } from '../utils/geolocation'
import { getTimezone } from '../utils/timezone'
import { setUniqIdOnRecommendation } from '../utils/recommendation'

const selectRecommendations = createSelector(
  state => state.data.recommendations,
  state => state.geolocation.latitude,
  state => state.geolocation.longitude,
  (recommendations, latitude, longitude) => {
    const fakeLastReco = {
      fakeLastReco: true,
      mediation: {
        firstThumbDominantColor: [205, 54, 70],
        frontText:
          'Vous avez parcouru toutes les offres. Revenez bientôt pour découvrir les nouveautés.',
        id: 'fin',
        thumbCount: 1,
        thumbUrls: [`${ROOT_PATH}/splash-finReco@2x.png`],
        tutoIndex: -1,
      },
      mediationId: 'fin',
      uniqId: 'tuto_-1',
    }
    // RECOMMENDATION MUST HAVE MEDIATION AND/OR OFFER CHILDREN
    // AND THAT IS A CRITERION TO MAKE THEM UNIQ
    let filteredRecommendations = recommendations.map(setUniqIdOnRecommendation)
    filteredRecommendations = filteredRecommendations.filter(
      recommendation => recommendation.uniqId
    )
    // filteredRecommendations.length = Math.min(filteredRecommendations.length,7)
    filteredRecommendations = uniqBy(
      filteredRecommendations,
      recommendation => recommendation.uniqId
    ).concat([fakeLastReco])

    // NOW WE CAN GIVE OTHER PROPERTIES TO THE GOOD SHAPED RECO
    filteredRecommendations = filteredRecommendations.map(
      (recommendation, index) => {
        const { mediation, offer } = recommendation
        const { eventOrThing, eventId, thingId, venue } = offer || {}

        // thumbUrl
        let thumbUrl
        const firstThumbDominantColor =
          get(mediation, 'firstThumbDominantColor') ||
          get(eventOrThing, 'firstThumbDominantColor')
        const mediationId = get(mediation, 'id')
        if (get(mediation, 'thumbCount')) {
          thumbUrl = get(
            mediation,
            'thumbUrls[0]',
            `${THUMBS_URL}/mediations/${mediationId}`
          )
        } else if (eventId && get(offer, 'eventOrThing.thumbCount')) {
          thumbUrl = get(
            eventOrThing,
            'thumbUrls[0]',
            `${THUMBS_URL}/events/${eventId}`
          )
        } else if (thingId && get(offer, 'eventOrThing.thumbCount')) {
          thumbUrl = get(
            eventOrThing,
            'thumbUrls[0]',
            `${THUMBS_URL}/things/${thingId}`
          )
        }

        let distance
        if (!latitude || !longitude || !offer || !venue) {
          distance = '-'
        } else {
          const distanceInMeters = computeDistanceInMeters(
            latitude,
            longitude,
            venue.latitude,
            venue.longitude
          )
          distance = humanizeDistance(distanceInMeters)
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
