export const getDiscoveryPath = (offer, mediation = '', toVerso = false) => {
  const offerId =
    typeof offer === 'string'
      ? offer
      : typeof offer === 'object'
        ? offer.id
        : 'tuto'
  const mediationId =
    typeof mediation === 'string'
      ? mediation
      : typeof mediation === 'object'
        ? mediation.id
        : ''
  const eventId =
    offer &&
    typeof offer === 'object' &&
    offer.eventOccurence &&
    offer.eventOccurence.eventId
  let url = `/decouverte/${offerId}/${mediationId}`
  if (toVerso) {
    url += '?to=verso'
  }
  if (eventId !== undefined) {
    url += `#${eventId}`
  }
  return url
}

export default getDiscoveryPath
