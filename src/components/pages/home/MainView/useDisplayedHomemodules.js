import { parse } from 'query-string'
import { useEffect, useState } from 'react'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { fetchHomepage } from '../../../../vendor/contentful/contentful'
import { parseAlgoliaParameters } from './domain/parseAlgoliaParameters'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'

const shouldModuleBeDisplayed = algoliaMapping => module => {
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
  const [fetchingError, setFetchingError] = useState(false)

  useEffect(() => {
    const { entryId } = parse(history.location.search)
    fetchHomepage({ entryId })
      .then(setModules)
      .catch(() => setFetchingError(true))
  }, [history.location.search])

  useEffect(() => {
    if (modules.length) {
      const fetchAlgoliaModules = async () =>
        await Promise.all(
          modules
            .filter(module => module instanceof Offers || module instanceof OffersWithCover)
            .map(async ({ algolia: parameters, moduleId }) => {
              const parsedParameters = parseAlgoliaParameters({ geolocation, parameters })
              if (!parsedParameters) return

              const response = await fetchAlgolia(parsedParameters)
              return { moduleId, parsedParameters, ...response }
            })
        )

      fetchAlgoliaModules().then(algoliaModules => {
        const mapping = {}
        algoliaModules.filter(Boolean).forEach(({ moduleId, nbHits, hits, parsedParameters }) => {
          mapping[moduleId] = { nbHits, hits, parsedParameters }
        })
        setAlgoliaMapping(mapping)
      })
    }
  }, [modules, geolocation])

  return {
    displayedModules: modules.filter(shouldModuleBeDisplayed(algoliaMapping)),
    fetchingError,
    algoliaMapping,
  }
}

export default useDisplayedHomemodules
