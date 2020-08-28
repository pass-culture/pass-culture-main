import { getStateKeyFromApiPath } from './getStateKeyFromApiPath'

export function getStateKeyFromUrl(url) {
  const apiPath = url
    .split('/')
    .slice(3)
    .join('/')
  return getStateKeyFromApiPath(apiPath)
}
