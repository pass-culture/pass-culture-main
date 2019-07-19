import { isEmpty } from '../utils/strings'

const isValid = user =>
  !(
    !user ||
    Array.isArray(user) ||
    typeof user !== 'object' ||
    typeof user.id !== 'string' ||
    !user.id
  )

export const getShareURL = (user, offerId = '', mediationId = '') => {
  if (!isValid(user)) return false
  if (isEmpty(offerId)) return false
  if (isEmpty(mediationId)) return false

  const { id } = user
  const origin = window.location.origin
  return `${origin}/decouverte/${offerId}/${mediationId}?shared_by=${id}`
}

export default getShareURL
