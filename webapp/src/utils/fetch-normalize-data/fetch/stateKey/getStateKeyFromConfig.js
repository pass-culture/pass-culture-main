import { getStateKeyFromApiPath } from './getStateKeyFromApiPath'
import { getStateKeyFromUrl } from './getStateKeyFromUrl'

export function getStateKeyFromConfig(config) {
  const { apiPath, url } = config

  if (config.stateKey === null) return null

  return (
    config.stateKey ||
    (apiPath && getStateKeyFromApiPath(apiPath)) ||
    (url && getStateKeyFromUrl(url))
  )
}
