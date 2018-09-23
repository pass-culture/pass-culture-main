const isValid = (location, user) =>
  !(
    !location ||
    !user ||
    Array.isArray(location) ||
    Array.isArray(user) ||
    typeof location !== 'object' ||
    typeof user !== 'object' ||
    typeof location.search !== 'string' ||
    typeof user.id !== 'string' ||
    !user.id
  )

/**
 * @param  {[type]}  location    React Router location object
 * @param  {[type]}  user        PC Store object
 * @param  {Boolean} [url=false] Only for Units Tests | window.location.href
 * @return {String}
 */
export const getShareURL = (location, user, url = false) => {
  if (!isValid(location, user)) return false
  const { id } = user
  const { search } = location
  const href = url || window.location.href
  const hasQuery = href.indexOf('?') !== -1
  const nextSearch = `${(hasQuery && '&') || '?'}shared_by=${id}`
  const shareSearch = `${search || ''}${nextSearch}`
  // suppr du search pour avoir la base
  const baseShareURL = (hasQuery && href.replace(search, '')) || href
  return `${baseShareURL}${shareSearch}`
}

export default getShareURL
