import getStateKeyFromApiPath from './getStateKeyFromApiPath'

function getStateKeyFromUrl(url) {
  const apiPath = url
    .split('/')
    .slice(3)
    .join('/')
  return getStateKeyFromApiPath(apiPath)
}

export default getStateKeyFromUrl
