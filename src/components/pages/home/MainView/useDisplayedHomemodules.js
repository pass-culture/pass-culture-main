import { getModulesToDisplay, getRecommendationModule } from './useDisplayedHomeModules.utils'
import useHomeAlgoliaModules from './useHomeAlgoliaModules'
import useHomepageModules from './useHomepageModules'
import { useHomeRecommendedHits } from './useRecommendedHits'

const useDisplayedHomemodules = (history, geolocation) => {
  // 1. Get the list of modules from contentful
  const homepageModules = useHomepageModules(history)
  const { modules } = homepageModules

  // 2. Get the hits and nbHits for each algolia module
  const algoliaModules = useHomeAlgoliaModules(modules, geolocation)
  const { algoliaMapping } = algoliaModules

  // 3. Get the offers for the recommended hits
  const recommendedHits = useHomeRecommendedHits(getRecommendationModule(modules))

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
