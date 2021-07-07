import { useEffect, useState } from 'react'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { parseAlgoliaParameters } from './domain/parseAlgoliaParameters'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'

const useHomeSearchModules = (offerModules, geolocation) => {
  const [algoliaMapping, setAlgoliaMapping] = useState({})
  const [isError, setIsError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (offerModules.length) {
      const fetchAlgoliaModules = async () => {
        const algoliaModules = await Promise.all(
          offerModules
            .filter(module => module instanceof Offers || module instanceof OffersWithCover)
            .map(async ({ algolia: parameters, moduleId }) => {
              const parsedParameters = parseAlgoliaParameters({ geolocation, parameters })
              if (!parsedParameters) return

              const response = await fetchAlgolia(parsedParameters)
              return { moduleId, parsedParameters, ...response }
            })
        )
        const mapping = {}
        algoliaModules.filter(Boolean).forEach(({ moduleId, nbHits, hits, parsedParameters }) => {
          mapping[moduleId] = { nbHits, hits, parsedParameters }
        })
        setAlgoliaMapping(mapping)
      }

      try {
        fetchAlgoliaModules()
      } catch (error) {
        setIsError(true)
      } finally {
        setIsLoading(false)
      }
    }
  }, [offerModules, geolocation])

  return {
    isError,
    isLoading,
    algoliaMapping,
  }
}

export default useHomeSearchModules
