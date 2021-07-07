import { getModulesToDisplay, getRecommendationModule } from './useDisplayedHomeModules.utils'
import useHomeSearchModules from './useHomeSearchModules'
import useHomepageModules from './useHomepageModules'
import { useHomeRecommendedHits } from './useRecommendedHits'

const useDisplayedHomemodules = (history, geolocation, userId, useAppSearch) => {
  // 1. Get the list of modules from contentful
  const homepageModules = useHomepageModules(history)
  const { modules } = homepageModules

  // 2. Get the hits and nbHits for each algolia module
  const algoliaModules = useHomeSearchModules(modules, geolocation)
  const { algoliaMapping } = algoliaModules

  // 3. Get the offers for the recommended hits
  const recommendationModule = getRecommendationModule(modules)
  const recommendedHits = useHomeRecommendedHits(
    recommendationModule,
    geolocation,
    userId,
    useAppSearch
  )

  // 4. Reconcile the three and filter the modules that will eventually be displayed
  const displayedModules = getModulesToDisplay(modules, algoliaMapping, recommendedHits)

  return {
    displayedModules,
    isError: homepageModules.isError || algoliaModules.isError,
    isLoading: homepageModules.isLoading || algoliaModules.isLoading,
    algoliaMapping,
    recommendedHits,
  }
}

export default useDisplayedHomemodules
