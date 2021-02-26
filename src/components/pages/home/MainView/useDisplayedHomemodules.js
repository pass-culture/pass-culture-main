import { getModulesToDisplay } from './useDisplayedHomeModules.utils'
import useHomeAlgoliaModules from './useHomeAlgoliaModules'
import useHomepageModules from './useHomepageModules'

const useDisplayedHomemodules = (history, geolocation) => {
  // 1. Get the list of modules from contentful
  const homepageModules = useHomepageModules(history)
  const { modules } = homepageModules

  // 2. Get the hits and nbHits for each algolia module
  const algoliaModules = useHomeAlgoliaModules(modules, geolocation)
  const { algoliaMapping } = algoliaModules

  // 3. Reconcile the two and filter the modules that will eventually be displayed
  const displayedModules = getModulesToDisplay(modules, algoliaMapping)

  return {
    displayedModules,
    isError: homepageModules.isError || algoliaModules.isError,
    isLoading: homepageModules.isLoading || algoliaModules.isLoading,
    algoliaMapping,
  }
}

export default useDisplayedHomemodules
