export const getOfferIdAndMediationIdAndCoordinatesApiPathQueryString = (
  match,
  currentRecommendation,
  coordinates
) => {
  const isValid = match && typeof match === 'object' && !Array.isArray(match)
  if (!isValid) return ''

  let { params: { mediationId, offerId } = {} } = match || {}
  const { longitude: longitude, latitude: latitude } = coordinates || {}

  offerId = typeof offerId === 'string' && offerId.trim() !== '' && offerId
  mediationId = typeof mediationId === 'string' && mediationId.trim() !== '' && mediationId

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
