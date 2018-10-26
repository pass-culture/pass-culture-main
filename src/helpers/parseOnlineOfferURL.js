import isAbsoluteUrl from 'is-absolute-url'

import { isEmpty, isString } from '../utils/strings'

// NOTE -> pas de tests sur le defaultPrefix
export const parseOnlineOfferURL = (url, defaultPrefix = 'https://') => {
  const isvalid = url && isString(url) && !isEmpty(url)
  // si ca buggue ca buggue.
  if (!isvalid) return url
  if (isAbsoluteUrl(url)) return url
  let result = url.trim()
  const containsSlash = result.indexOf('//') === 0 || result.indexOf('/') === 0
  if (containsSlash) {
    const isdoubled = result.slice(0, 2) === '//'
    const index = Number(isdoubled) + 1
    result = result.slice(index)
  }
  result = `${defaultPrefix}${result}`
  return result
}

export default parseOnlineOfferURL
