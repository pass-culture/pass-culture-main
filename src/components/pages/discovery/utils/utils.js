import selectCurrentRecommendation from '../selectors/selectCurrentRecommendation'
import selectNextRecommendation from '../selectors/selectNextRecommendation'
import selectPreviousRecommendation from '../selectors/selectPreviousRecommendation'

export const MINIMUM_DELAY_BEFORE_RELOAD_RECOMMENDATION_3_HOURS = 3 * 60 * 60 * 1000

export const isDiscoveryStartupUrl = match => {
  const { params, url } = match
  const { mediationId } = params

  if (!mediationId) {
    return true
  }

  const matchDiscoveryStartupPathRegex = /\/decouverte((\/)|(\/tuto\/fin\/?))?$/
  const matches = url.match(matchDiscoveryStartupPathRegex)
  if (!matches) {
    return false
  }
  return matches.length > 0
}

export const checkIfShouldReloadRecommendationsBecauseOfLongTime = state => {
  const now = Date.now()
  const { lastRecommendationsRequestTimestamp } = state || 0
  if (!lastRecommendationsRequestTimestamp) return true
  return (
    now >= lastRecommendationsRequestTimestamp + MINIMUM_DELAY_BEFORE_RELOAD_RECOMMENDATION_3_HOURS
  )
}

const noop = () => {}
export const getRecommendationSelectorByCardPosition = position => {
  switch (position) {
    case 'current':
      return selectCurrentRecommendation
    case 'previous':
      return selectPreviousRecommendation
    case 'next':
      return selectNextRecommendation
    default:
      return noop
  }
}
