export function getUrlFromConfig(config) {
  let { url } = config
  const { apiPath, rootUrl } = config
  if (!url) {
    url = `${rootUrl}/${apiPath.replace(/^\//, '')}`
  }
  return url
}

export default getUrlFromConfig
