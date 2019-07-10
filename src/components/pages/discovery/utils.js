export const MINIMUM_DELAY_BEFORE_RELOAD_RECOMMENDATION_3_HOURS =
  3 * 60 * 60 * 1000

export const isDiscoveryStartupPathname = str => {
  if (!str || typeof str !== 'string') return false
  const matchDiscoveryStartupPathRegex = /\/decouverte((\/)|(\/tuto\/fin\/?))?$/
  const matches = str.match(matchDiscoveryStartupPathRegex)
  return matches && matches.length > 0
}

export const checkIfShouldReloadRecommendations = state => {
  const now = Date.now()
  const { lastRecommendationsRequestTimestamp } = state || 0
  if (!lastRecommendationsRequestTimestamp) return true
  return (
    now >=
    lastRecommendationsRequestTimestamp +
      MINIMUM_DELAY_BEFORE_RELOAD_RECOMMENDATION_3_HOURS
  )
}
