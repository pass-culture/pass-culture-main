import BusinessPane from './domain/ValueObjects/BusinessPane'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'
import RecommendationPane from './domain/ValueObjects/RecommendationPane'

export const getModulesToDisplay = (modules, algoliaMapping, recommendedHits) =>
  modules.filter(module => {
    if (module instanceof BusinessPane) return true
    if (module instanceof ExclusivityPane) return true
    if (module instanceof RecommendationPane) {
      const { minOffers = 0 } = module.display || {}
      return recommendedHits.length >= minOffers
    }

    if (module.moduleId in algoliaMapping) {
      const { hits = [], nbHits = 0 } = algoliaMapping[module.moduleId] || {}
      const { minOffers = 0 } = module.display || {}
      const atLeastOneHit = hits.length > 0
      const minOffersHasBeenReached = nbHits >= minOffers
      return atLeastOneHit && minOffersHasBeenReached
    }

    return false
  })

export const getRecommendationModule = modules =>
  modules.find(module => module instanceof RecommendationPane)
