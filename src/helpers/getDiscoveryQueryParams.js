export const getDiscoveryQueryParams = match => {
  const { offerId, mediationId: mediationIdOrViewId } = match.params || {}
  const isTutoOffer = offerId === 'tuto'
  const isView =
    mediationIdOrViewId === 'booking' || mediationIdOrViewId === 'verso'

  const mediationId = !isView && mediationIdOrViewId
  const params = [
    // si il ne s'agit pas d'un tuto alors is s'agit d'une offre
    (!isTutoOffer && offerId && `offerId=${offerId}`) || null,
    (mediationId && `mediationId=${mediationId}`) || null,
  ]
  const query = params.filter(s => s).join('&')
  return query
}

export default getDiscoveryQueryParams
