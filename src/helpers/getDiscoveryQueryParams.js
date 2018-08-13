export const getDiscoveryQueryParams = match => {
  const { offerId, mediationId } = match.params
  const query = [
    (offerId && offerId !== 'tuto' && `offerId=${offerId}`) || null,
    (mediationId && `mediationId=${mediationId}`) || null,
  ]
    .filter(s => s)
    .join('&')
  return query
}

export default getDiscoveryQueryParams
