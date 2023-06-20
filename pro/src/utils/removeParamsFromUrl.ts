export const removeParamsFromUrl = (url: string): string => {
  if (url.indexOf('?') === -1) return url
  return url.substring(0, url.indexOf('?'))
}
