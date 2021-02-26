import { useEffect, useState } from 'react'

import { humanizeId } from '../../../../utils/dehumanizeId/dehumanizeId'
import { fetchAlgoliaHits } from '../../../../vendor/algolia/algolia'

const recommendedIds = [
  '145932',
  '145945',
  '145926',
  '145900',
  '145909',
  '145929',
  '145902',
  '145941',
  '145906',
  '145944',
]

export const useHomeRecommendedHits = () => {
  const [offerIds, setOfferIds] = useState([])
  const [recommendedHits, setRecommendedHits] = useState([])

  useEffect(() => {
    // TODO (#6271) get the actual ids from the recommendation API
    const ids = recommendedIds.map(id => humanizeId(+id)).filter(id => typeof id === 'string')
    setOfferIds(ids)
  }, [])

  useEffect(() => {
    if (offerIds.length > 0) {
      fetchAlgoliaHits(offerIds).then(({ results }) => {
        const hitsWithCover = results.filter(hit => hit && hit.offer && !!hit.offer.thumbUrl)
        setRecommendedHits(hitsWithCover)
      })
    }
  }, [offerIds])

  return recommendedHits
}
