export function parseUrlParams(urlParams: URLSearchParams) {
  const queryParams: Record<string, string | string[]> = {}
  urlParams.forEach((value, key) => {
    if (queryParams[key]) {
      if (!Array.isArray(queryParams[key])) {
        queryParams[key] = [queryParams[key]]
      }
      queryParams[key].push(value)
    } else {
      queryParams[key] = value
    }
  })
  return queryParams
}
