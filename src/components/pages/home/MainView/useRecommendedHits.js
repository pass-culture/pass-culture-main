import { useEffect, useState } from 'react'
import { RECOMMENDATION_ENDPOINT, RECOMMENDATION_TOKEN } from '../../../../utils/config'

import { fetchAlgoliaHits } from '../../../../vendor/algolia/algolia'

export const useHomeRecommendedHits = (recommendationModule, geolocation, userId) => {
  const recommendedIds = useRecommendedOfferIds(recommendationModule, geolocation, userId)
  return useRecommendedHits(recommendedIds || [])
}

const useRecommendedOfferIds = (recommendationModule, geolocation, userId) => {
  const [offerIds, setOfferIds] = useState([])

  useEffect(() => {
    if (recommendationModule) {
      fetch(getRecommendationEndpoint(userId, geolocation))
        .then(res => res.json())
        .then(({ recommended_offers: ids }) => {
          setOfferIds(ids)
        })
        .catch(() => [])
    }
    // we don't want to refetch the ids on each new position
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recommendationModule, userId])

  return offerIds
}

const useRecommendedHits = ids => {
  const [recommendedHits, setRecommendedHits] = useState([])

  useEffect(() => {
    if (ids.length > 0) {
      fetchAlgoliaHits(ids).then(({ results }) => {
        const hitsWithCover = results.filter(hit => hit && hit.offer && !!hit.offer.thumbUrl)
        setRecommendedHits(hitsWithCover)
      })
    }
  }, [ids])

  return recommendedHits
}

export const getRecommendationEndpoint = (userId, position) => {
  if (!userId) return undefined
  const endpoint = `${RECOMMENDATION_ENDPOINT}/recommendation/${userId}?token=${RECOMMENDATION_TOKEN}`

  const { longitude = null, latitude = null } = position || {}

  const parameters =
    typeof longitude === 'number' && typeof latitude === 'number'
      ? `&longitude=${longitude}&latitude=${latitude}`
      : ''

  return `${endpoint}${parameters}`
}
