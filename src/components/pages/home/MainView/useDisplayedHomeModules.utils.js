import BusinessPane from './domain/ValueObjects/BusinessPane'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'

export const getModulesToDisplay = (modules, algoliaMapping) =>
  modules.filter(module => {
    if (module instanceof BusinessPane) return true
    if (module instanceof ExclusivityPane) return true

    if (module.moduleId in algoliaMapping) {
      const { hits = [], nbHits = 0 } = algoliaMapping[module.moduleId] || {}
      const atLeastOneHit = hits.length > 0
      const minOffersHasBeenReached = nbHits >= module.display.minOffers
      return atLeastOneHit && minOffersHasBeenReached
    }

    return false
  })
