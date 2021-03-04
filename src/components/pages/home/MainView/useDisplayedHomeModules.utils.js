import BusinessPane from './domain/ValueObjects/BusinessPane'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'
import RecommendationPane from './domain/ValueObjects/RecommendationPane'

export const getModulesToDisplay = (modules, algoliaMapping, recommendedHits) =>
  modules.filter(module => {
    if (module instanceof BusinessPane) return true
    if (module instanceof ExclusivityPane) return true
    if (module instanceof RecommendationPane) {
      return recommendedHits.length >= module.display.minOffers
    }

    if (module.moduleId in algoliaMapping) {
      const { hits = [], nbHits = 0 } = algoliaMapping[module.moduleId] || {}
      const atLeastOneHit = hits.length > 0
      const minOffersHasBeenReached = nbHits >= module.display.minOffers
      return atLeastOneHit && minOffersHasBeenReached
    }

    return false
  })

export const getRecommendationModule = modules =>
  modules.find(module => module instanceof RecommendationPane)
