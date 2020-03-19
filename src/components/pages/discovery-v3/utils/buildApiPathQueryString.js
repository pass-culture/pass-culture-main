import { DEFAULT_VIEW_IDENTIFIERS } from './utils'

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

export const getCoordinatesApiPathQueryString = coordinates => {
  const { longitude, latitude } = coordinates || {}

  if (longitude && latitude) {
    const queryParameters = { longitude, latitude }
    return Object.keys(queryParameters)
      .map(transformKeysToQueryString(queryParameters))
      .join('&')
  }
  return ''
}

function transformKeysToQueryString(queryParameters) {
  return key => key + '=' + queryParameters[key]
}
