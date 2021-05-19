export const queryParamsFromOfferer = location => {
  const queryParams = new URLSearchParams(location.search)
  const isOfferer = queryParams.has('structure')
  const isVenue = queryParams.has('lieu')

  return {
    structure: isOfferer ? queryParams.get('structure') : '',
    lieu: isVenue ? queryParams.get('lieu') : '',
  }
}
