export function getStateKeyFromApiPath(apiPath) {
  return apiPath
    .replace(/^\/|\/$/g, '')
    .split('?')[0]
    .split('/')[0]
}
