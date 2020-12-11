import { parse } from 'query-string'
import { useEffect, useState } from 'react'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { fetchHomepage } from '../../../../vendor/contentful/contentful'
import { parseAlgoliaParameters } from './domain/parseAlgoliaParameters'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'

export const shouldModuleBeDisplayed = algoliaMapping => module => {
  if (module instanceof Offers || module instanceof OffersWithCover) {
    const { hits = [], nbHits = 0 } = algoliaMapping[module.moduleId] || {}
    const atLeastOneHit = hits.length > 0
    const minOffersHasBeenReached = nbHits >= module.display.minOffers
    return atLeastOneHit && minOffersHasBeenReached
  }
  return true
}

const useDisplayedHomemodules = (history, geolocation) => {
  const [modules, setModules] = useState([])
  const [algoliaMapping, setAlgoliaMapping] = useState({})
  const [isError, setIsError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const parsedSearch = parse(history.location.search)
    setIsError(false)
    setIsLoading(true)
    fetchHomepage({ entryId: parsedSearch ? parsedSearch.entryId : '' })
      .then(setModules)
      .catch(() => setIsError(true))
  }, [history.location.search])

  useEffect(() => {
    if (modules.length) {
      const fetchAlgoliaModules = async () => {
        const algoliaModules = await Promise.all(
          modules
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
        setIsLoading(false)
      }

      try {
        fetchAlgoliaModules()
      } catch (error) {
        setIsError(true)
        setIsLoading(false)
      }
    }
  }, [modules, geolocation])

  return {
    displayedModules: modules.filter(shouldModuleBeDisplayed(algoliaMapping)),
    isError,
    isLoading,
    algoliaMapping,
  }
}

export default useDisplayedHomemodules
