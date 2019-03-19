const URL_SPLITTER = '/'
const QUERY_SPLITTER = '&'
export const DEFAULT_VIEW_IDENTIFIERS = ['booking', 'verso', 'tuto']

export const getQueryParams = (match, currentRecommendation) => {
  const isValid = match && typeof match === 'object' && !Array.isArray(match)
  if (!isValid) return ''

  const { offerId: pOfferId, mediationId: pMediationId } =
    match.params || match || {}

  // offerId
  const offerId =
    typeof pOfferId === 'string' &&
    pOfferId.trim() !== '' &&
    !DEFAULT_VIEW_IDENTIFIERS.includes(pOfferId) &&
    pOfferId

  // mediationId
  const mediationId =
    typeof pMediationId === 'string' &&
    pMediationId.trim() !== '' &&
    !DEFAULT_VIEW_IDENTIFIERS.includes(pMediationId) &&
    pMediationId

  const isSameRecoAsMatchParams = currentRecommendation &&
  currentRecommendation.mediationId === mediationId &&
  currentRecommendation.offerId === offerId
  if (isSameRecoAsMatchParams) return ''

  const params = [
    // si il ne s'agit pas d'un tuto alors is s'agit d'une offre
    (offerId && `offerId=${offerId}`) || null,
    // mediationId/tuto fixed in commit:
    // https://github.com/betagouv/pass-culture-api/commit/719f19a
    (mediationId && `mediationId=${mediationId}`) || null,
  ]
  const query = params.filter(s => s).join(QUERY_SPLITTER)
  return query
}

export const getQueryURL = match => {
  const params = getQueryParams(match)
  if (!params) return ''
  const queryurl = params
    .split(QUERY_SPLITTER)
    .map(str => str.split('='))
    .map(arr => arr[1])
    .join(URL_SPLITTER)
  return queryurl
}

export default getQueryParams
