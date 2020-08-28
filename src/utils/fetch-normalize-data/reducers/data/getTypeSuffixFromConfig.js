export function getTypeSuffixFromConfig(config) {
  const { apiPath, method = 'GET', stateKey, tag, url } = config
  return `${method}_${stateKey || apiPath || url}${
    tag ? `_${tag}` : ''
  }`.toUpperCase()
}

export default getTypeSuffixFromConfig
