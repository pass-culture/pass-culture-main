/**
 * Permet d'exclure un terme d'un résultat
 * @param  {String} term A comma splitted string
 * @return {String}
 */
const excludeTermRegExp = term =>
  (term && `\\b([a-z0-9]+)\\b(?<!${term.split(',').join('|')})`) || ''

// FIXME -> peut etre deplacer les termes dans des constantes
const tutoExcludeExp = new RegExp(excludeTermRegExp('tuto'), 'g')
const viewExcludeExp = new RegExp(excludeTermRegExp('booking|verso'), 'g')

export const getDiscoveryQueryParams = match => {
  const { offerId, mediationId } = match.params || {}
  const isTutoOffer = !offerId || !offerId.match(tutoExcludeExp)
  const isView = mediationId && !mediationId.match(viewExcludeExp)
  const hasMediationId = mediationId && !isView
  const params = [
    // si il ne s'agit pas d'un tuto alors is s'agit d'une offre
    (!isTutoOffer && offerId && `offerId=${offerId}`) || null,
    (hasMediationId && `mediationId=${mediationId}`) || null,
  ]
  const query = params.filter(s => s).join('&')
  return query
}

export default getDiscoveryQueryParams
