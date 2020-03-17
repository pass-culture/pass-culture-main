import selectCurrentRecommendation from '../selectors/selectCurrentRecommendation'
import selectNextRecommendation from '../selectors/selectNextRecommendation'
import selectPreviousRecommendation from '../selectors/selectPreviousRecommendation'

export const DEFAULT_VIEW_IDENTIFIERS = ['fin', 'tuto', 'vide']
export const MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS = 3 * 60 * 60 * 1000
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

export const getOfferIdAndMediationIdAndCoordinatesApiPathQueryString = (
  match,
  currentRecommendation,
  coordinates
) => {
  const isValid = match && typeof match === 'object' && !Array.isArray(match)
  if (!isValid) return ''

  const { params: { mediationId: pMediationId, offerId: pOfferId } = {} } = match || {}
  const { longitude: longitude, latitude: latitude } = coordinates || {}

  const offerId =
    typeof pOfferId === 'string' &&
    pOfferId.trim() !== '' &&
    !DEFAULT_VIEW_IDENTIFIERS.includes(pOfferId) &&
    pOfferId

  const mediationId =
    typeof pMediationId === 'string' &&
    pMediationId.trim() !== '' &&
    !DEFAULT_VIEW_IDENTIFIERS.includes(pMediationId) &&
    pMediationId

  const isSameRecoAsMatchParams =
    currentRecommendation &&
    currentRecommendation.mediationId === mediationId &&
    currentRecommendation.offerId === offerId

  if (isSameRecoAsMatchParams) return ''

  const params = [
    (offerId && `offerId=${offerId}`) || null,
    (mediationId && `mediationId=${mediationId}`) || null,
    (longitude && `longitude=${longitude}`) || null,
    (latitude && `latitude=${latitude}`) || null,
  ]

  const query = params.filter(s => s).join('&')
  return query
}
