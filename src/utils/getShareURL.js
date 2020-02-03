import isEmpty from './strings/isEmpty'

const isValid = user => user && typeof user === 'object' && user.id && typeof user.id === 'string'

const getShareURL = (user = {}, offerId = '', mediationId = 'vide') => {
  if (!isValid(user)) return null
  if (isEmpty(offerId)) return null

  const { id } = user
  const origin = window.location.origin
  return `${origin}/offre/details/${offerId}/${mediationId}?shared_by=${id}`
}

export default getShareURL
